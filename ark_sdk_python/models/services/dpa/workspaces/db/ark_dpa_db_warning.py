from enum import Enum


class ArkDPADBWarning(str, Enum):
    NoCertificates = 'no_certificates'
    NoSecrets = 'no_secrets'
    AnyError = 'any_error'
