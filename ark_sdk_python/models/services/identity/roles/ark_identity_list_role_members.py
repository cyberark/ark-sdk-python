from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityListRoleMembers(ArkModel):
    role_name: Optional[str] = Field(description='Name of the role to get members of')
    role_id: Optional[str] = Field(description='ID of the role to get members of')
