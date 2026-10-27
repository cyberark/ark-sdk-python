from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetVaultGroup(ArkModel):
    group_id: int = Field(description='ID of the group to get')
