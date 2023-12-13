from typing import Any


class ArkException(Exception):
    pass


class ArkAuthException(ArkException):
    pass


class ArkNonInteractiveException(ArkException):
    pass


class ArkInterruptedException(ArkException):
    pass


class ArkValidationException(ArkException):
    pass


class ArkNotFoundException(ArkException):
    pass


class ArkNotSupportedException(ArkException):
    pass


class ArkServiceException(ArkException):
    def __init__(self, error: Any, *args: object) -> None:
        self.error = error
        super().__init__(error, *args)
