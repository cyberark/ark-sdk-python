from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_add_policy import ArkSIABaseAddPolicy
from ark_sdk_python.models.services.sia.policies.db.ark_sia_db_authorization_rule import ArkSIADBAuthorizationRule
from ark_sdk_python.models.services.sia.policies.db.ark_sia_db_providers import ArkSIADBProvidersData


class ArkSIADBAddPolicy(ArkSIABaseAddPolicy):
    providers_tags: List[str] = Field(description='Policy tags to use as filters for the assets in the rules', default_factory=list)
    providers_data: Optional[ArkSIADBProvidersData] = Field(
        default=None, description='Policy providers data containing database assets of different types'
    )
    user_access_rules: Optional[List[ArkSIADBAuthorizationRule]] = Field(
        default=None, description='Authorization rules of the policy describing how and who can access the assets'
    )
