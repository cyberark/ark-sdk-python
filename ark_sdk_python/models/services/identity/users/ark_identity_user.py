from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkPresentableModel


class ArkIdentityUser(ArkPresentableModel):
    user_id: str = Field(description='User identifier')
    username: str = Field(description='Name of the user')
    display_name: str = Field(description='Display name of the user')
    email: Optional[str] = Field(description='Email of the user')
    mobile_number: Optional[str] = Field(description='Mobile number of the user')
    roles: Optional[List[str]] = Field(description='Roles of the user')
    last_login: Optional[datetime] = Field(description='Last login of the user')
