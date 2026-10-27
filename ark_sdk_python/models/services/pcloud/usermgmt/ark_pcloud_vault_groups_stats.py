from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudVaultGroupsStats(ArkModel):
    groups_count: int = Field(description='Overall group count')
    group_types_count: Dict[str, int] = Field(description='Group count per type')
