from enum import Enum


class ArkUAPPolicyType(str, Enum):
    RECURRING = 'Recurring'
    ONDEMAND = 'OnDemand'
