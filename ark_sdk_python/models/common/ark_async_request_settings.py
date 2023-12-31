from typing import Final, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel

DEFAULT_POLL_SLEEP_TIME_SECONDS: Final[int] = 1
DEFAULT_PROGRESS_TICK_COUNT_SECONDS: Final[int] = 3


class ArkAsyncRequestSettings(ArkModel):
    poll_sleep_time: Optional[int] = Field(
        description='Poll sleep time in seconds on waiting for async request to complete',
        alias='Poll Sleep Time',
        default=DEFAULT_POLL_SLEEP_TIME_SECONDS,
    )
    progress_tick_count: Optional[int] = Field(
        description='Every how much time to notify for progression in seconds',
        alias='Progress Tick Count',
        default=DEFAULT_PROGRESS_TICK_COUNT_SECONDS,
    )
    poll_allow_refreshable_connection: Optional[bool] = Field(
        description='Allow connection refresh for long poll operations',
        alias='Poll Allow Refreshable Connection',
        default=False,
    )
