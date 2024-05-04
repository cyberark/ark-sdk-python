from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudActivateTargetPlatform(ArkModel):
    target_platform_id: int = Field(description='ID of the platform to activate')
