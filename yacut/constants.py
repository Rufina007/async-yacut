import string

SHORT_ID_LENGTH = 6
SHORT_ID_MAX_LENGTH = 16
SHORT_ID_ALPHABET = string.ascii_letters + string.digits
SHORT_ID_PATTERN = r'^[A-Za-z0-9]+$'
RESERVED_SHORT_IDS = ('files',)
MAX_SHORT_ID_ATTEMPTS = 10

DUPLICATE_SHORT_ID_MSG = 'Предложенный вариант короткой ссылки уже существует.'
INVALID_SHORT_ID_MSG = 'Указано недопустимое имя для короткой ссылки'
CUSTOM_ID_LENGTH_MSG = f'Не более {SHORT_ID_MAX_LENGTH} символов'
CUSTOM_ID_FORMAT_MSG = 'Допустимы только латинские буквы и цифры'
SHORT_ID_GENERATION_ERROR_MSG = (
    'Не удалось сгенерировать уникальный короткий идентификатор'
)
