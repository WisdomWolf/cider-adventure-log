from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import BEVERAGE_TYPES, Barcode, Beverage, Rating

main_bp = Blueprint('main', __name__)


def _type_field_types(model_class) -> dict:
    """Maps each column name local to a Beverage subclass's own table (i.e.
    excluding inherited base-table columns) to its Python type, so incoming
    form values can be coerced correctly."""
    mapper = sa_inspect(model_class)
    return {
        column.name: column.type.python_type
        for column in mapper.local_table.columns
        if column.name != 'id'
    }


def _extract_detail_kwargs(model_class, data) -> dict:
    kwargs = {}
    for field, python_type in _type_field_types(model_class).items():
        if field not in data:
            continue
        raw = data.get(field)
        if raw is None or raw == '':
            kwargs[field] = None
            continue
        try:
            kwargs[field] = python_type(raw)
        except (TypeError, ValueError):
            kwargs[field] = raw
    return kwargs


@main_bp.route('/api/beverages/<int:beverage_id>', methods=['GET'])
def get_beverage_details(beverage_id):
    beverage = Beverage.query.get(beverage_id)
    if not beverage:
        return jsonify({"message": "Beverage not found"}), 404

    return jsonify(beverage.to_detail_dict())


@main_bp.route('/api/beverages', methods=['GET'])
def get_beverages():
    query = Beverage.query
    beverage_type = request.args.get('type')
    if beverage_type:
        query = query.filter_by(type=beverage_type)

    beverages = query.all()
    return jsonify([b.to_summary_dict() for b in beverages])


@main_bp.route('/api/beverages', methods=['POST'])
@login_required
def add_beverage():
    data = request.form
    beverage_type = data.get('type')
    model_class = BEVERAGE_TYPES.get(beverage_type)
    if not model_class:
        return jsonify({"message": "Invalid or missing beverage type."}), 400

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

    beverage = model_class(
        brand=data['brand'],
        name=data['name'],
        description=data.get('description'),
        image=image,
        **_extract_detail_kwargs(model_class, data),
    )

    db.session.add(beverage)

    if barcode := data.get('barcode'):
        new_barcode = Barcode(code=barcode, beverage=beverage)
        db.session.add(new_barcode)

    db.session.commit()
    return jsonify({"message": "Beverage added successfully!"}), 201


@main_bp.route('/api/beverages/<int:beverage_id>/ratings', methods=['POST'])
@login_required
def add_rating(beverage_id):
    beverage = Beverage.query.get(beverage_id)
    if not beverage:
        return jsonify({"message": "Beverage not found"}), 404

    data = request.json
    score = data.get('score')
    comment = data.get('comment', '')
    attributes = data.get('attributes') or None

    if not score or not (1 <= score <= 5):
        return jsonify({"message": "Invalid rating score. Must be between 1 and 5."}), 400

    rating = Rating(
        score=score,
        comment=comment,
        beverage_id=beverage_id,
        user_id=current_user.id,
        attributes=attributes,
    )
    db.session.add(rating)
    db.session.commit()

    return jsonify({"message": "Rating added successfully!"}), 201


@main_bp.route('/api/beverages/<int:beverage_id>', methods=['DELETE'])
@login_required
def delete_beverage(beverage_id):
    beverage = Beverage.query.get(beverage_id)
    if beverage:
        db.session.delete(beverage)
        db.session.commit()
        return jsonify({"message": "Beverage deleted successfully!"}), 200
    return jsonify({"message": "Beverage not found"}), 404


@main_bp.route('/api/beverages/<int:beverage_id>/barcodes', methods=['POST'])
@login_required
def add_barcode(beverage_id):
    data = request.json
    beverage = Beverage.query.get_or_404(beverage_id)
    new_barcode = Barcode(code=data['code'], beverage=beverage)
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


@main_bp.route('/api/beverages/<int:beverage_id>', methods=['PUT'])
@login_required
def update_beverage(beverage_id):
    beverage = Beverage.query.get_or_404(beverage_id)
    data = request.form

    # Update basic beverage information
    beverage.brand = data['brand']
    beverage.name = data['name']
    beverage.description = data.get('description')

    for field, value in _extract_detail_kwargs(type(beverage), data).items():
        setattr(beverage, field, value)

    # Handle image update
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file:
            beverage.image = image_file.read()
    elif 'image_url' in data and data['image_url']:
        try:
            import requests
            response = requests.get(data['image_url'])
            if response.status_code == 200:
                beverage.image = response.content
        except Exception as e:
            return jsonify({"message": "Failed to fetch image from URL", "error": str(e)}), 400

    # Handle barcode update if provided
    if barcode := data.get('barcode'):
        # Remove existing barcodes
        for existing_barcode in beverage.barcodes:
            db.session.delete(existing_barcode)
        # Add new barcode
        new_barcode = Barcode(code=barcode, beverage=beverage)
        db.session.add(new_barcode)

    try:
        db.session.commit()
        return jsonify({"message": "Beverage updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update beverage", "error": str(e)}), 400
