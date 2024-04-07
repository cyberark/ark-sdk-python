from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityGetAuthenticationProfile(ArkModel):
    auth_profile_id: Optional[str] = Field(description='Gets the profile by id')
    auth_profile_name: Optional[str] = Field(description='Gets the profile by name')
