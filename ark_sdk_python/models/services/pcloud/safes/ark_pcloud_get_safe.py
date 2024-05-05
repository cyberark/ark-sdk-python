from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetSafe(ArkModel):
    safe_id: str = Field(description='Safe id to get details for')
