from enum import Enum


class ArkSIARuleStatus(str, Enum):
    Enabled = 'Enabled'
    Disabled = 'Disabled'
    Draft = 'Draft'
    Expired = 'Expired'
