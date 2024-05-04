from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudDeactivateTargetPlatform(ArkModel):
    target_platform_id: int = Field(description='ID of the platform to deactivate')
