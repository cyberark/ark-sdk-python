from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkPCloudBaseVaultGroup(ArkCamelizedModel):
    group_name: str = Field(description='Name of the group')
    description: Optional[str] = Field(default=None, description='Description about the group')
    location: Optional[str] = Field(description='Location of the group', default='\\')


class ArkPCloudVaultGroupMember(ArkCamelizedModel):
    username: str = Field(description='Username of the member')
    id: int = Field(description='ID of the member')


class ArkPCloudVaultGroup(ArkPCloudBaseVaultGroup):
    id: int = Field(description='ID of the group')
    group_type: str = Field(description='Type of the group')
    members: Optional[List[ArkPCloudVaultGroupMember]] = Field(default=None, description='Members of the group')
