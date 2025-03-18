from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkPresentableModel


class ArkIdentityUser(ArkPresentableModel):
    user_id: str = Field(description='User identifier')
    username: str = Field(description='Name of the user')
    display_name: Optional[str] = Field(description='Display name of the user')
    email: Optional[str] = Field(default=None, description='Email of the user')
    mobile_number: Optional[str] = Field(default=None, description='Mobile number of the user')
    roles: Optional[List[str]] = Field(default=None, description='Roles of the user')
    last_login: Optional[datetime] = Field(default=None, description='Last login of the user')
