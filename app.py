from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=True)
    barcode = db.Column(db.Text, nullable=True)
    ratings = db.relationship('Rating', backref='product', lazy=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Routes
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = []
    for product in products:
        average_rating = (
            sum(rating.score for rating in product.ratings) / len(product.ratings)
            if product.ratings else None
        )
        result.append({
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "type": product.type,
            "barcode": product.barcode,
            "average_rating": average_rating,
            "ratings": [{"user": r.user, "score": r.score, "comment": r.comment} for r in product.ratings]
        })
    return jsonify(result)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json

    # Validate required fields
    if not all(key in data for key in ['name', 'brand', 'type', 'barcode']):
        return jsonify({"message": "Missing required fields"}), 400

    # Create and save the product
    product = Product(
        name=data['name'],
        brand=data['brand'],
        type=data['type'],
        barcode=data['barcode']
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added successfully!"}), 201


@app.route('/products/<int:product_id>/ratings', methods=['POST'])
def add_rating(product_id):
    data = request.json
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    rating = Rating(user=data['user'], score=data['score'], comment=data.get('comment'), product_id=product_id)
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
