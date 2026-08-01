import io
from datetime import datetime

import openpyxl
from flask import Blueprint, jsonify, request
from flask_login import login_required

from .extensions import db
from .models import CiderDetails, Rating, User

import_bp = Blueprint('imports', __name__, url_prefix='/api/imports')

# Column layout of the historical "Cider Adventure Log" Google Forms export.
# This importer is purpose-built for that one known shape, not a generic
# spreadsheet mapper.
COLUMNS = {
    'timestamp': 0,
    'brand': 1,
    'flavor': 2,
    'purchase_location': 3,
    'rating': 4,
    'last_tasted': 5,
    'comments': 6,
    'consumption_location': 8,
    'consumption_method': 9,
    'other_medium': 10,
    'name': 11,
}


def _norm(value):
    return ' '.join(str(value).split()) if value not in (None, '') else ''


def _norm_key(value):
    return _norm(value).lower()


def _iso(value):
    return value.isoformat() if isinstance(value, datetime) else None


def parse_workbook(file_stream):
    wb = openpyxl.load_workbook(file_stream, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))

    empty_summary = {'total_rows': 0, 'beverage_count': 0, 'rating_count': 0, 'rows_without_rating': 0}
    if not rows:
        return {'beverages': [], 'names': [], 'summary': empty_summary}

    header = rows[0]
    brand_col = COLUMNS['brand']
    flavor_col = COLUMNS['flavor']
    if (
        len(header) <= flavor_col
        or _norm_key(header[brand_col]) != 'brand'
        or _norm_key(header[flavor_col]) != 'flavor'
    ):
        raise ValueError(
            "This doesn't look like the expected Cider Adventure Log export "
            "(expected 'Brand' and 'Flavor' as the 2nd and 3rd columns)."
        )

    groups = {}
    names = set()
    total_rows = 0
    rating_count = 0
    rows_without_rating = 0

    for row in rows[1:]:
        if row is None or not any(row):
            continue

        brand = _norm(row[COLUMNS['brand']])
        flavor = _norm(row[COLUMNS['flavor']])
        if not brand or not flavor:
            continue
        total_rows += 1

        key = (_norm_key(brand), _norm_key(flavor))
        group = groups.setdefault(key, {'brand': brand, 'name': flavor, 'ratings': []})

        raw_name = _norm(row[COLUMNS['name']])
        if raw_name:
            names.add(raw_name)

        score = row[COLUMNS['rating']]
        if score is None:
            rows_without_rating += 1
            continue

        consumption_method = _norm(row[COLUMNS['consumption_method']])
        other_medium = _norm(row[COLUMNS['other_medium']])
        if consumption_method.lower().startswith('other') and other_medium:
            consumption_method = other_medium

        tasted_at = row[COLUMNS['last_tasted']] or row[COLUMNS['timestamp']]

        group['ratings'].append({
            'raw_name': raw_name or None,
            'score': int(score),
            'comment': _norm(row[COLUMNS['comments']]) or None,
            'purchase_location': _norm(row[COLUMNS['purchase_location']]) or None,
            'consumption_location': _norm(row[COLUMNS['consumption_location']]) or None,
            'consumption_method': consumption_method or None,
            'tasted_at': _iso(tasted_at),
        })
        rating_count += 1

    beverages = sorted(groups.values(), key=lambda g: (g['brand'].lower(), g['name'].lower()))

    return {
        'beverages': beverages,
        'names': sorted(names, key=str.lower),
        'summary': {
            'total_rows': total_rows,
            'beverage_count': len(beverages),
            'rating_count': rating_count,
            'rows_without_rating': rows_without_rating,
        },
    }


@import_bp.route('/preview', methods=['POST'])
@login_required
def preview_import():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'message': 'No file uploaded.'}), 400

    try:
        result = parse_workbook(io.BytesIO(file.read()))
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'Failed to parse spreadsheet.', 'error': str(e)}), 400

    return jsonify(result)


@import_bp.route('/commit', methods=['POST'])
@login_required
def commit_import():
    data = request.json or {}
    beverages_payload = data.get('beverages') or []
    name_map = data.get('name_map') or {}

    # Re-group by normalized brand/name in case the client edited text to
    # merge two preview groups into one beverage.
    merged = {}
    for group in beverages_payload:
        brand = _norm(group.get('brand'))
        name = _norm(group.get('name'))
        if not brand or not name:
            continue
        key = (_norm_key(brand), _norm_key(name))
        target = merged.setdefault(key, {'brand': brand, 'name': name, 'ratings': []})
        target['ratings'].extend(group.get('ratings') or [])

    beverages_created = 0
    ratings_created = 0
    ratings_skipped = 0

    try:
        for group in merged.values():
            beverage = CiderDetails(brand=group['brand'], name=group['name'])
            db.session.add(beverage)
            beverages_created += 1

            for rating in group['ratings']:
                raw_name = rating.get('raw_name')
                user_id = name_map.get(raw_name) if raw_name else None
                user = db.session.get(User, user_id) if user_id else None
                score = rating.get('score')

                if not user or not score or not (1 <= score <= 5):
                    ratings_skipped += 1
                    continue

                created_at = None
                if rating.get('tasted_at'):
                    try:
                        created_at = datetime.fromisoformat(rating['tasted_at'])
                    except ValueError:
                        created_at = None

                db.session.add(Rating(
                    beverage=beverage,
                    user_id=user.id,
                    score=score,
                    comment=rating.get('comment'),
                    purchase_location=rating.get('purchase_location'),
                    consumption_location=rating.get('consumption_location'),
                    consumption_method=rating.get('consumption_method'),
                    created_at=created_at,
                ))
                ratings_created += 1

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Import failed.', 'error': str(e)}), 400

    return jsonify({
        'beverages_created': beverages_created,
        'ratings_created': ratings_created,
        'ratings_skipped': ratings_skipped,
    }), 201
