from aenum import MultiValueEnum


class ArkUAPStatusType(str, MultiValueEnum):
    ACTIVE = 'Active', 'ACTIVE', 'active'
    SUSPENDED = 'Suspended', 'SUSPENDED', 'suspended'
    EXPIRED = 'Expired', 'EXPIRED', 'expired'
    VALIDATING = 'Validating', 'VALIDATING', 'validating'
    ERROR = 'Error', 'ERROR', 'error'
    WARNING = 'Warning', 'WARNING', 'warning'
