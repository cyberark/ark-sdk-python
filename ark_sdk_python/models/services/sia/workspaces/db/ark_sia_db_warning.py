from enum import Enum


class ArkSIADBWarning(str, Enum):
    NoCertificates = 'no_certificates'
    NoSecrets = 'no_secrets'
    AnyError = 'any_error'
