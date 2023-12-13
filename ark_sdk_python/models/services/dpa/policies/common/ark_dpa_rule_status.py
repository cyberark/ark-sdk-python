from enum import Enum


class ArkDPARuleStatus(str, Enum):
    Enabled = 'Enabled'
    Disabled = 'Disabled'
    Draft = 'Draft'
    Expired = 'Expired'
