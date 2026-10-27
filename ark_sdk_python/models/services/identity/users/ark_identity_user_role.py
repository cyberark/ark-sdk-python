from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUserRole(ArkModel):
    role_id: str = Field(description='Identifier of the role')
    role_name: Optional[str] = Field(description='Display name of the role', default=None)
    name: Optional[str] = Field(description='Name of the role as identity returns it, can hold its id', default=None)
    distinguished_name: Optional[str] = Field(description='Distinguished name of the role', default=None)
