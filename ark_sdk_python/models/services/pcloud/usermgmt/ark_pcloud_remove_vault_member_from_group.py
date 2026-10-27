from typing import Union

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudRemoveVaultMemberFromGroup(ArkModel):
    group_id: int = Field(description='Group id to remove the mmeber from')
    member_id: Union[int, str] = Field(description='The member to remove')
