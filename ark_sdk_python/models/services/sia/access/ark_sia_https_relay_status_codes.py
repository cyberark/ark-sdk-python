from enum import IntEnum


class ArkSIAHttpsRelayStatusCodes(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    DOWNLOADED = 2


class ArkSIAHttpsRelayModeCodes(IntEnum):
    AVAILABLE = 0
    JOB_IN_PROGRESS = 1
    SUSPENDED = 2
    ROTATION_JOB_IN_PROGRESS = 3
