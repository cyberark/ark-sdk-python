from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_policy import ArkDPABasePolicy
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_authorization_rule import ArkDPADBAuthorizationRule
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_providers import ArkDPADBProvidersData


class ArkDPADBPolicy(ArkDPABasePolicy):
    providers_tags: List[str] = Field(description='Policy tags', default_factory=list)
    providers_data: ArkDPADBProvidersData = Field(description='Policy providers data')
    user_access_rules: Optional[List[ArkDPADBAuthorizationRule]] = Field(description='Authorization rules of the policy')
