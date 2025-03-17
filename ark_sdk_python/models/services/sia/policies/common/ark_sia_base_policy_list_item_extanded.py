from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_authorization_rule_extended import ArkSIABaseAuthorizationRuleExtended
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policy_list_item import ArkSIABasePolicyListItemBase
from ark_sdk_python.models.services.sia.policies.vm import ArkSIAVMProvidersDict


class ArkSIABasePolicyListItemExtended(ArkSIABasePolicyListItemBase):
    providers_data: Optional[ArkSIAVMProvidersDict] = Field(default=None, description='Provider data of the policy')
    start_date: Optional[str] = Field(default=None, description='Start date of the policy')
    end_date: Optional[str] = Field(default=None, description='Expiration date of the policy')
    user_access_rules: Optional[List[ArkSIABaseAuthorizationRuleExtended]] = Field(
        default=None, description='Authorization rules of the policy'
    )
