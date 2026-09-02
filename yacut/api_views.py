import re

from flask import jsonify, request, url_for

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id

SHORT_ID_PATTERN = re.compile(r'^[A-Za-z0-9]+$')
DUPLICATE_MSG = 'Предложенный вариант короткой ссылки уже существует.'
INVALID_SHORT_ID_MSG = 'Указано недопустимое имя для короткой ссылки'


def is_valid_short_id(short_id):
    return len(short_id) <= 16 and SHORT_ID_PATTERN.match(short_id)


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    custom_id = data.get('custom_id')
    if custom_id:
        if not is_valid_short_id(custom_id):
            raise InvalidAPIUsage(INVALID_SHORT_ID_MSG)
        if URLMap.query.filter_by(short=custom_id).first() is not None:
            raise InvalidAPIUsage(DUPLICATE_MSG)
        short = custom_id
    else:
        short = get_unique_short_id()
    url_map = URLMap(original=data['url'], short=short)
    db.session.add(url_map)
    db.session.commit()
    return jsonify({
        'url': url_map.original,
        'short_link': url_for('redirect_view', short_id=short, _external=True)
    }), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original})
