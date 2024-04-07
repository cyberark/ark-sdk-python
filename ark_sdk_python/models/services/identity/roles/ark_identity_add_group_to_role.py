from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityAddGroupToRole(ArkModel):
    group_name: str = Field(description='Group name to add to the role')
    role_name: str = Field(description='Name of the role to add the group to')
