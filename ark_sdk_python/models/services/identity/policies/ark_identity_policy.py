from typing import Any, Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel
from ark_sdk_python.models.services.identity.policies.ark_identity_authentication_profile import ArkIdentityAuthenticationProfile


class ArkIdentityPolicyDirectoryService(ArkTitleizedModel):
    display_name_short: str = Field(description='Display name of the directory service')
    directory_service_uuid: str = Field(description='UUID of the directory', alias='directoryServiceUuid')


class ArkIdentityPolicy(ArkTitleizedModel):
    auth_profiles: List[ArkIdentityAuthenticationProfile] = Field(description="Auth profiles set for the policy")
    description: str = Field(description='Description of the policy')
    directory_services: List[ArkIdentityPolicyDirectoryService] = Field(description='Directory services of the policy')
    path: str = Field(description='Path of the policy')
    policy_modifiers: List[str] = Field(description='Modifiers of the policy')
    radius_client_list: Optional[List[str]] = Field(default=None, description='Client list integrated with radius on the policy')
    radius_server_list: Optional[List[str]] = Field(default=None, description='Server list integrated with radius on the policy')
    rev_stamp: str = Field(description='Timestamp of the revision')
    risk_analysis_levels: Dict[str, Any] = Field(description='Risk analysis info')
    settings: Dict[str, Any] = Field(description='Settings of the policy')
    version: int = Field(description='Version of the policy')
