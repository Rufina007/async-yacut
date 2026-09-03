from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .exceptions import (
    InvalidShortIDError, ShortIDExistsError, ShortIDGenerationError
)
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    try:
        url_map = URLMap.create(data['url'], data.get('custom_id'))
    except (
        InvalidShortIDError, ShortIDExistsError, ShortIDGenerationError
    ) as error:
        raise InvalidAPIUsage(str(error)) from error
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.get_by_short_id(short_id)
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify(url=url_map.original)
