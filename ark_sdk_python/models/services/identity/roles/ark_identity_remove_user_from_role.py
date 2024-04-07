from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityRemoveUserFromRole(ArkModel):
    username: str = Field(description='Username to remove from the role')
    role_name: str = Field(description='Name of the role to remove the user from')
