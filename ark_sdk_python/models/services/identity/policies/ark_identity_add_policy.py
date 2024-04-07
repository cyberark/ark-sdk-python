from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityAddPolicy(ArkModel):
    policy_name: str = Field(description='Name of the policy to create')
    description: str = Field(description='Description of the policy', default="")
    role_names: List[str] = Field(description='Roles to associate to the policy')
    auth_profile_name: str = Field(description='Authentication profile to assoicate to the policy')
    settings: Optional[Dict[str, Any]] = Field(description='Settings of the policy')
