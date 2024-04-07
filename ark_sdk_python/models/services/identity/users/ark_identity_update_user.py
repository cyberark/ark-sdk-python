from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUpdateUser(ArkModel):
    user_id: Optional[str] = Field(description='Users id that we change the details for')
    username: Optional[str] = Field(description='Username that we change the details for')
    new_username: Optional[str] = Field(description='Name of the user to change')
    display_name: Optional[str] = Field(description='Display name of the user to change')
    email: Optional[str] = Field(description='Email of the user to change')
    mobile_number: Optional[str] = Field(description='Mobile number of the user to change')
