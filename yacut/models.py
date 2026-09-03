import re
from datetime import datetime
from random import choice

from flask import url_for

from yacut import db
from yacut.constants import (
    MAX_SHORT_ID_ATTEMPTS, RESERVED_SHORT_IDS, SHORT_ID_ALPHABET,
    SHORT_ID_LENGTH, SHORT_ID_MAX_LENGTH, SHORT_ID_PATTERN
)


class ShortIDExistsError(Exception):
    pass


class InvalidShortIDError(Exception):
    pass


def generate_short_id():
    return ''.join(choice(SHORT_ID_ALPHABET) for _ in range(SHORT_ID_LENGTH))


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(
        db.String(SHORT_ID_MAX_LENGTH), unique=True, nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_short_link(self):
        return url_for('redirect_view', short_id=self.short, _external=True)

    def to_dict(self):
        return dict(url=self.original, short_link=self.get_short_link())

    @staticmethod
    def is_valid_short_id(short_id):
        return (
            len(short_id) <= SHORT_ID_MAX_LENGTH
            and re.match(SHORT_ID_PATTERN, short_id) is not None
        )

    @staticmethod
    def is_short_id_taken(short_id):
        return (
            short_id in RESERVED_SHORT_IDS
            or URLMap.query.filter_by(short=short_id).first() is not None
        )

    @classmethod
    def get_by_short_id(cls, short_id):
        return cls.query.filter_by(short=short_id).first()

    @classmethod
    def get_unique_short_id(cls):
        for _ in range(MAX_SHORT_ID_ATTEMPTS):
            short_id = generate_short_id()
            if not cls.is_short_id_taken(short_id):
                return short_id
        raise RuntimeError(
            'Не удалось сгенерировать уникальный короткий идентификатор'
        )

    @classmethod
    def create(cls, original, custom_id=None):
        if custom_id:
            if not cls.is_valid_short_id(custom_id):
                raise InvalidShortIDError()
            if cls.is_short_id_taken(custom_id):
                raise ShortIDExistsError()
            short = custom_id
        else:
            short = cls.get_unique_short_id()
        url_map = cls(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map
