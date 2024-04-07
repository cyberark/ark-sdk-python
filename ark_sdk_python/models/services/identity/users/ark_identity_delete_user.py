from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityDeleteUser(ArkModel):
    user_id: Optional[str] = Field(description='User ID to delete')
    username: Optional[str] = Field(description='Username to delete')
