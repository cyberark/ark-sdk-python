from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityDeleteRole(ArkModel):
    role_name: Optional[str] = Field(default=None, description='Role name to delete')
    role_id: Optional[str] = Field(default=None, description='Role id to delete')
