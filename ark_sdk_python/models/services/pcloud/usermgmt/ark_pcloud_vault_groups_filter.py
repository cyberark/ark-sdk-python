from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkPCloudVaultGroupsFilter(ArkModel):
    group_type: Optional[str] = Field(default=None, description='Type of the groups to filter')
    group_name: Optional[str] = Field(default=None, description='Name of the group to filter')
    sort: Optional[str] = Field(default=None, description='Sort by value')
    search: Optional[str] = Field(default=None, description='Search string')
