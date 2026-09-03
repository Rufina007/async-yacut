from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from yacut.constants import (
    CUSTOM_ID_FORMAT_MSG, CUSTOM_ID_LENGTH_MSG, SHORT_ID_MAX_LENGTH,
    SHORT_ID_PATTERN
)


class ShortenerForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(1, SHORT_ID_MAX_LENGTH, message=CUSTOM_ID_LENGTH_MSG),
            Regexp(SHORT_ID_PATTERN, message=CUSTOM_ID_FORMAT_MSG)
        ]
    )
    submit = SubmitField('Создать')


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[DataRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Загрузить')
