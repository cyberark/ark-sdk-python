import os
from typing import Final, Optional

from ark_sdk_python.common.ark_logger import LOG_LEVEL, LOGGER_STYLE

ARK_DISABLE_CERTIFICATE_VERIFICATION_ENV_VAR: Final[str] = 'ARK_DISABLE_CERTIFICATE_VERIFICATION'


class ArkSystemConfig:
    _NO_COLOR = False
    _IS_INTERACTIVE = True
    _IS_CERTIFICATE_VERIFICATION = True
    _IS_ALLOWING_OUTPUT = False
    _TRUSTED_CERT = None

    @staticmethod
    def disable_color():
        ArkSystemConfig._NO_COLOR = True

    @staticmethod
    def enable_color():
        ArkSystemConfig._NO_COLOR = False

    @staticmethod
    def is_coloring():
        return not ArkSystemConfig._NO_COLOR

    @staticmethod
    def enable_interactive():
        ArkSystemConfig._IS_INTERACTIVE = True

    @staticmethod
    def disable_interactive():
        ArkSystemConfig._IS_INTERACTIVE = False

    @staticmethod
    def is_interactive():
        return ArkSystemConfig._IS_INTERACTIVE

    @staticmethod
    def allow_output():
        ArkSystemConfig._IS_ALLOWING_OUTPUT = True

    @staticmethod
    def disallow_output():
        ArkSystemConfig._IS_ALLOWING_OUTPUT = False

    @staticmethod
    def is_allowing_output():
        return ArkSystemConfig._IS_ALLOWING_OUTPUT

    @staticmethod
    def enable_verbose_logging(log_level: Optional[str] = None):
        log_level = log_level or 'DEBUG'
        os.environ[LOG_LEVEL] = log_level

    @staticmethod
    def disable_verbose_logging() -> None:
        os.environ[LOG_LEVEL] = 'CRITICAL'

    @staticmethod
    def set_logger_style(logger_style: str) -> None:
        if logger_style in ['default']:
            os.environ[LOGGER_STYLE] = logger_style
        else:
            os.environ[LOGGER_STYLE] = 'default'

    @staticmethod
    def enable_certificate_verification() -> None:
        ArkSystemConfig._IS_CERTIFICATE_VERIFICATION = True

    @staticmethod
    def disable_certificate_verification() -> None:
        ArkSystemConfig._IS_CERTIFICATE_VERIFICATION = False

    @staticmethod
    def is_verifiying_certificates() -> bool:
        if ARK_DISABLE_CERTIFICATE_VERIFICATION_ENV_VAR in os.environ:
            return False
        return ArkSystemConfig._IS_CERTIFICATE_VERIFICATION

    @staticmethod
    def set_trusted_certificate(trusted_cert: str) -> None:
        ArkSystemConfig._TRUSTED_CERT = trusted_cert

    @staticmethod
    def trusted_certificate() -> str:
        return ArkSystemConfig._TRUSTED_CERT
