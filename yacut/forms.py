from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired, Length, Optional, Regexp, ValidationError
)

from .models import URLMap

SHORT_ID_PATTERN = r'^[A-Za-z0-9]*$'
DUPLICATE_MSG = 'Предложенный вариант короткой ссылки уже существует.'


class ShortenerForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(1, 16, message='Не более 16 символов'),
            Regexp(
                SHORT_ID_PATTERN,
                message='Допустимы только латинские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if not field.data:
            return
        if (
            field.data == 'files'
            or URLMap.query.filter_by(short=field.data).first() is not None
        ):
            raise ValidationError(DUPLICATE_MSG)


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[DataRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Загрузить')
