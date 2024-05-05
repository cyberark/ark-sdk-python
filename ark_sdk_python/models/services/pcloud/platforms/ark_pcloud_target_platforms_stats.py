from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudTargetPlatformsStats(ArkModel):
    target_platforms_count: int = Field(description='Overall target platforms amount')
    active_target_platforms_count: int = Field(description='Amount of active target platforms')
    target_platforms_count_by_system_type: Dict[str, int] = Field(description='Target platforms amount by system type')
