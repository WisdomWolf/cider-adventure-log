import base64

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.schema import UniqueConstraint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flavor = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)

    ratings = db.relationship('Rating', backref='product', lazy=True)

    # Add a conditional unique constraint for barcode
    # __table_args__ = (
    #     UniqueConstraint('barcode', name='uq_product_barcode', sqlite_where=db.text("barcode IS NOT NULL")),
    # )

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
        "name": product.name,
        "brand": product.brand,
        "type": product.type,
        "barcode": product.barcode,
        "description": product.description,
        "image": image_base64,
        "ratings": ratings,
        "average_rating": sum(r.score for r in product.ratings) / len(product.ratings) if product.ratings else None
    })


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "type": p.type,
            "barcode": p.barcode,
            "average_rating": sum(r.score for r in p.ratings) / len(p.ratings) if p.ratings else None
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
        name=data['name'],
        brand=data['brand'],
        type=data['type'],
        barcode=data.get('barcode'),
        description=data.get('description'),
        image=image
    )
    db.session.add(product)
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


@app.route('/products/<int:product_id>/average-rating', methods=['GET'])
def get_average_rating(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if not product.ratings:
        return jsonify({"average_rating": None}), 200

    average_rating = sum(rating.score for rating in product.ratings) / len(product.ratings)
    return jsonify({"average_rating": average_rating}), 200


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    average_rating = (
        sum(rating.score for rating in product.ratings) / len(product.ratings)
        if product.ratings else None
    )
    return jsonify({
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode,
        "average_rating": average_rating,
        "ratings": [{"user": r.user, "score": r.score, "comment": r.comment} for r in product.ratings]
    })


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
