from enum import IntEnum


class ArkAsyncStatus(IntEnum):
    StartedPolling = 0
    StillPolling = 1
    AsyncTaskUpdated = 2
    Successful = 4
    Failed = 8
    Timeout = 16
