from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetPlatform(ArkModel):
    platform_id: str = Field(description='Name of the platform')
