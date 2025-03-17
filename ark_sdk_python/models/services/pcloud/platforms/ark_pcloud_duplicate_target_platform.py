from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudDuplicateTargetPlatform(ArkModel):
    target_platform_id: int = Field(description='ID of the platform to duplicate')
    name: str = Field(description='New duplicated target platform name')
    description: Optional[str] = Field(description='New duplicated target platform description', default=None)
