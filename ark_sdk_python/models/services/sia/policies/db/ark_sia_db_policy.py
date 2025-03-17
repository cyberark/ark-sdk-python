from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policy import ArkSIABasePolicy
from ark_sdk_python.models.services.sia.policies.db.ark_sia_db_authorization_rule import ArkSIADBAuthorizationRule
from ark_sdk_python.models.services.sia.policies.db.ark_sia_db_providers import ArkSIADBProvidersData


class ArkSIADBPolicy(ArkSIABasePolicy):
    providers_tags: List[str] = Field(description='Policy tags', default_factory=list)
    providers_data: ArkSIADBProvidersData = Field(description='Policy providers data')
    user_access_rules: Optional[List[ArkSIADBAuthorizationRule]] = Field(default=None, description='Authorization rules of the policy')
