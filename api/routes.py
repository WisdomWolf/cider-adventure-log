import base64

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Barcode, Product, Rating

main_bp = Blueprint('main', __name__)


@main_bp.route('/api/products/<int:product_id>', methods=['GET'])
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


@main_bp.route('/api/products', methods=['GET'])
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


@main_bp.route('/api/products', methods=['POST'])
@login_required
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


@main_bp.route('/api/products/<int:product_id>/ratings', methods=['POST'])
@login_required
def add_rating(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    score = data.get('score')
    comment = data.get('comment', '')

    if not score or not (1 <= score <= 5):
        return jsonify({"message": "Invalid rating score. Must be between 1 and 5."}), 400

    rating = Rating(score=score, comment=comment, product_id=product_id, user_id=current_user.id)
    db.session.add(rating)
    db.session.commit()

    return jsonify({"message": "Rating added successfully!"}), 201


@main_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully!"}), 200
    return jsonify({"message": "Product not found"}), 404


@main_bp.route('/api/products/<int:product_id>/barcodes', methods=['POST'])
@login_required
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


@main_bp.route('/api/barcodes/<int:barcode_id>', methods=['DELETE'])
@login_required
def delete_barcode(barcode_id):
    barcode = Barcode.query.get_or_404(barcode_id)
    db.session.delete(barcode)
    db.session.commit()
    return jsonify({"message": "Barcode deleted successfully!"}), 200


@main_bp.route('/api/scan', methods=['POST'])
@login_required
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


@main_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.form

    # Update basic product information
    product.brand = data['brand']
    product.flavor = data['flavor']
    product.description = data.get('description')

    # Handle image update
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file:
            product.image = image_file.read()
    elif 'image_url' in data and data['image_url']:
        try:
            import requests
            response = requests.get(data['image_url'])
            if response.status_code == 200:
                product.image = response.content
        except Exception as e:
            return jsonify({"message": "Failed to fetch image from URL", "error": str(e)}), 400

    # Handle barcode update if provided
    if barcode := data.get('barcode'):
        # Remove existing barcodes
        for existing_barcode in product.barcodes:
            db.session.delete(existing_barcode)
        # Add new barcode
        new_barcode = Barcode(code=barcode, product=product)
        db.session.add(new_barcode)

    try:
        db.session.commit()
        return jsonify({"message": "Product updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update product", "error": str(e)}), 400
