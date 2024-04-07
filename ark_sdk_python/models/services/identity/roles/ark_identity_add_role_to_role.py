from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityAddRoleToRole(ArkModel):
    role_name_to_add: str = Field(description='Role name to add to the role')
    role_name: str = Field(description='Name of the role to add the role to')
