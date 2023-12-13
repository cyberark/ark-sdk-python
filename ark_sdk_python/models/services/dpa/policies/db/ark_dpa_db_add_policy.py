from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_add_policy import ArkDPABaseAddPolicy
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_authorization_rule import ArkDPADBAuthorizationRule
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_providers import ArkDPADBProvidersData


class ArkDPADBAddPolicy(ArkDPABaseAddPolicy):
    providers_tags: List[str] = Field(description='Policy tags to use as filters for the assets in the rules', default_factory=list)
    providers_data: Optional[ArkDPADBProvidersData] = Field(
        description='Policy providers data containing database assets of different types'
    )
    user_access_rules: Optional[List[ArkDPADBAuthorizationRule]] = Field(
        description='Authorization rules of the policy describing how and who can access the assets'
    )
