from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityAddUserToRole(ArkModel):
    username: str = Field(description='Username to add to the role')
    role_name: str = Field(description='Name of the role to add the user to')
