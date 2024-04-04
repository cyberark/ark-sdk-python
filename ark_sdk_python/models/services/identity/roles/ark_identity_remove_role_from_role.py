from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityRemoveRoleFromRole(ArkModel):
    role_name_to_remove: str = Field(description='Role name to remove from the role')
    role_name: str = Field(description='Name of the role to remove the role from')
