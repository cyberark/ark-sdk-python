from enum import Enum


class ArkSIATargetSetType(str, Enum):
    DOMAIN = 'Domain'
    SUFFIX = 'Suffix'
    TARGET = 'Target'
