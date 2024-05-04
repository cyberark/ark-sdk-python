from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.pcloud.platforms.ark_pcloud_platform import ArkPCloudPlatformType


class ArkPCloudPlatformsStats(ArkModel):
    platforms_count: int = Field(description='Overall platforms amount')
    platforms_count_by_type: Dict[ArkPCloudPlatformType, int] = Field(description='Platforms amount by type')
