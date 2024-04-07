from enum import Enum


class ArkIdentityPolicyOperationType(str, Enum):
    ENABLE = 'Global'
    DISABLE = 'Inactive'
