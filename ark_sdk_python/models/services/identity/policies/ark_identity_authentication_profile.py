from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkIdentityAuthenticationProfile(ArkTitleizedModel):
    challenges: List[str] = Field(description='List of challenges for the profile')
    id: Optional[str] = Field(description='Identifier of the profile', alias='ID')
    name: str = Field(description='Name of the profile')
    single_challenge_mechanisms: Optional[str] = Field(description='Single challenge mechanisms used')
    uuid: str = Field(description='UUID of the profile')
    additional_data: Dict[str, Any] = Field(description='Additional profile data')
