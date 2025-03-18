from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUpdateUser(ArkModel):
    user_id: Optional[str] = Field(default=None, description='Users id that we change the details for')
    username: Optional[str] = Field(default=None, description='Username that we change the details for')
    new_username: Optional[str] = Field(default=None, description='Name of the user to change')
    display_name: Optional[str] = Field(default=None, description='Display name of the user to change')
    email: Optional[str] = Field(default=None, description='Email of the user to change')
    mobile_number: Optional[str] = Field(default=None, description='Mobile number of the user to change')
