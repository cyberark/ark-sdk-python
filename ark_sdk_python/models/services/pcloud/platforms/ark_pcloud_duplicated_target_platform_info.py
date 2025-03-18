from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkPCloudDuplicatedTargetPlatformInfo(ArkTitleizedModel):
    id: int = Field(description='ID of the duplicated platform', alias='ID')
    platform_id: str = Field(description='Platform id of the duplicated platform', alias='PlatformID')
    name: str = Field(description='New duplicated target platform name')
    description: Optional[str] = Field(description='New duplicated target platform description', default=None)
