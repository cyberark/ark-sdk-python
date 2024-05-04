from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.pcloud.platforms.ark_pcloud_platform import ArkPCloudPlatformType


class ArkPCloudPlatformsFilter(ArkModel):
    active: Optional[bool] = Field(description='Filter only active or inactive platforms')
    platform_type: Optional[ArkPCloudPlatformType] = Field(description='Filter platforms by type')
    platform_name: Optional[str] = Field(description='Filter platforms by name')
