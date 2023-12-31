from typing import Final

VALID_DATE_REGEX: Final[str] = r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$'
VALID_LOGIN_NAME_REGEX = r'^[\w.+\-]+?$'
VALID_LOGIN_MAX_LENGTH = 256
