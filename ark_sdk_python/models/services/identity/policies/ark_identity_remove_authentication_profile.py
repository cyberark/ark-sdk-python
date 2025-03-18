from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityRemoveAuthenticationProfile(ArkModel):
    auth_profile_id: Optional[str] = Field(default=None, description='Remove the profile by id')
    auth_profile_name: Optional[str] = Field(default=None, description='Remove the profile by name')
