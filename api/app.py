import base64
from datetime import datetime
from typing import Optional

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Models
class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str]
    flavor: Mapped[str]
    description: Mapped[Optional[str]]
    image = mapped_column(db.LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    ratings: Mapped[list["Rating"]] = db.relationship(back_populates='product')
    barcodes: Mapped[list["Barcode"]] = db.relationship(
        back_populates='product',
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def average_rating(self) -> float:
        if self.ratings:
            return sum(r.score for r in self.ratings) / len(self.ratings)
        else:
            return None


class Barcode(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey('product.id'),
        nullable=False
    )
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    product: Mapped["Product"] = db.relationship(back_populates="barcodes")


class Rating(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey('product.id'),
        nullable=False
    )
    score: Mapped[int]
    comment: Mapped[Optional[str]]
    purchase_location: Mapped[Optional[str]]
    consumption_location: Mapped[Optional[str]]
    consumption_method: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    product: Mapped["Product"] = db.relationship(back_populates="ratings")


# Routes
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    # Convert the binary image data to a Base64 string (if it exists)
    image_base64 = None
    if product.image:
        image_base64 = base64.b64encode(product.image).decode('utf-8')

    ratings = [
        {"id": r.id, "score": r.score, "comment": r.comment}
        for r in product.ratings
    ]

    return jsonify({
        "id": product.id,
        "flavor": product.flavor,
        "brand": product.brand,
        "barcodes": [
                {"id": barcode.id, "code": barcode.code}
                for barcode in product.barcodes
        ],
        "description": product.description,
        "image": image_base64,
        "ratings": ratings,
        "average_rating": product.average_rating
    })


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "brand": p.brand,
            "flavor": p.flavor,
            "barcodes": [
                {"id": barcode.id, "code": barcode.code}
                for barcode in p.barcodes
            ],
            "average_rating": p.average_rating
        }
        for p in products
    ])


@app.route('/products', methods=['POST'])
def add_product():
    data = request.form
    image = None

    # Handle image upload
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file:
            image = image_file.read()

    # Handle image URL
    if 'image_url' in data and data['image_url']:
        try:
            import requests
            response = requests.get(data['image_url'])
            if response.status_code == 200:
                image = response.content  # Download and store the image as binary data
        except Exception as e:
            return jsonify({"message": "Failed to fetch image from URL", "error": str(e)}), 400

    product = Product(
        brand=data['brand'],
        flavor=data['flavor'],
        description=data.get('description'),
        image=image
    )
    
    db.session.add(product)

    if barcode := data.get('barcode'):
        new_barcode = Barcode(code=barcode, product=product)
        db.session.add(new_barcode)

    db.session.commit()
    return jsonify({"message": "Product added successfully!"}), 201


@app.route('/products/<int:product_id>/ratings', methods=['POST'])
def add_rating(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    score = data.get('score')
    comment = data.get('comment', '')

    if not score or not (1 <= score <= 5):
        return jsonify({"message": "Invalid rating score. Must be between 1 and 5."}), 400

    rating = Rating(score=score, comment=comment, product_id=product_id)
    db.session.add(rating)
    db.session.commit()

    return jsonify({"message": "Rating added successfully!"}), 201


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully!"}), 200
    return jsonify({"message": "Product not found"}), 404


@app.route('/products/<int:product_id>/barcodes', methods=['POST'])
def add_barcode(product_id):
    data = request.json
    product = Product.query.get_or_404(product_id)
    new_barcode = Barcode(code=data['code'], product=product)
    try:
        db.session.add(new_barcode)
        db.session.commit()
        return jsonify({"id": new_barcode.id, "code": new_barcode.code}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This barcode already exists."}), 400


@app.route('/barcodes/<int:barcode_id>', methods=['DELETE'])
def delete_barcode(barcode_id):
    barcode = Barcode.query.get_or_404(barcode_id)
    db.session.delete(barcode)
    db.session.commit()
    return jsonify({"message": "Barcode deleted successfully!"}), 200


@app.route('/scan', methods=['POST'])
def scan_barcode():
    from pyzbar.pyzbar import decode
    from PIL import Image
    import io

    file = request.files['image']
    image = Image.open(io.BytesIO(file.read()))
    decoded_objects = decode(image)
    if decoded_objects:
        return jsonify({"barcode": decoded_objects[0].data.decode('utf-8')})
    return jsonify({"message": "No barcode detected"}), 400


# Initialize the database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Initialize the database
    app.run(debug=True, host='0.0.0.0', port=5050)
