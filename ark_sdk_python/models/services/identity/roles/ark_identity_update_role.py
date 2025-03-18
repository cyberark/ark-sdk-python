from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUpdateRole(ArkModel):
    role_name: Optional[str] = Field(default=None, description='Role name to update')
    role_id: Optional[str] = Field(default=None, description='Role id to update')
    new_role_name: Optional[str] = Field(default=None, description='New role name to update to')
    description: Optional[str] = Field(default=None, description='New description of the role')
