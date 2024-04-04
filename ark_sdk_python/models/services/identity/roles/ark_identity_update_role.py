from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUpdateRole(ArkModel):
    role_name: Optional[str] = Field(description='Role name to update')
    role_id: Optional[str] = Field(description='Role id to update')
    new_role_name: Optional[str] = Field(description='New role name to update to')
    description: Optional[str] = Field(description='New description of the role')
