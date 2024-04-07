from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityRole(ArkModel):
    role_id: str = Field(description='Identifier of the role')
    role_name: str = Field(description='Name of the role')
