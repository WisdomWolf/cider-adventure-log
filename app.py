import base64

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.ext.hybrid import hybrid_property


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    flavor = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)

    ratings = db.relationship('Rating', backref='product', lazy=True)
    barcodes = db.relationship(
        'Barcode',
        backref='product',
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def average_rating(self) -> float:
        if self.ratings:
            return sum(r.score for r in self.ratings) / len(self.ratings)
        else:
            return None


class Barcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False, unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)


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

    ratings = [{"id": r.id, "score": r.score, "comment": r.comment} for r in product.ratings]

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
    data = request.form  # Use form data for handling file uploads
    image = None

    # Handle image upload
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file:
            image = image_file.read()  # Read the binary data of the uploaded image

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
    db.session.add(new_barcode)
    db.session.commit()
    return jsonify({"id": new_barcode.id, "code": new_barcode.code}), 201


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
