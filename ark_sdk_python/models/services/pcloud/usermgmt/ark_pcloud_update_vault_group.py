from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudUpdateVaultGroup(ArkCamelizedModel):
    group_id: int = Field(description='ID of the group to update')
    group_name: Optional[str] = Field(description='Group name to update')
