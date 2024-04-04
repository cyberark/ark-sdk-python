from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityRemoveGroupFromRole(ArkModel):
    group_name: str = Field(description='Group name to remove from the role')
    role_name: str = Field(description='Name of the role to remove the group from')
