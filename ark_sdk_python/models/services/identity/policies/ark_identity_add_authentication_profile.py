from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityAddAuthenticationProfile(ArkModel):
    auth_profile_name: str = Field(description='Name of the profile')
    first_challenges: List[str] = Field(description='List of first challenges for the profile, i,e "UP,SMS"')
    second_challenges: Optional[List[str]] = Field(default=None, description='List of second challenges for the profile, i,e "UP,SMS"')
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description='Additional auth profile data')
    duration_in_minutes: int = Field(description='Duration of auth profile', default=30)
