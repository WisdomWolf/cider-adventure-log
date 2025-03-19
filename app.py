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
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

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
    product = Product.query.get_or_404(product_id)
    ratings = Rating.query.filter_by(product_id=product_id).all()

    return jsonify({
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "type": product.type,
        "barcode": product.barcode,
        "description": product.description,
        "image_url": product.image_url,
        "average_rating": sum(r.score for r in ratings) / len(ratings) if ratings else None,
        "ratings": [{"score": r.score, "comment": r.comment} for r in ratings]
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
