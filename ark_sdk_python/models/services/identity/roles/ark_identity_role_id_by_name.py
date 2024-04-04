from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityRoleIdByName(ArkModel):
    role_name: str = Field(description='Role name to find the id for')
