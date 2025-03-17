from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_rule_status import ArkSIARuleStatus


class ArkSIABasePolicyListItemBase(ArkCamelizedModel):
    policy_id: str = Field(description='ID of the policy')
    policy_name: str = Field(description='Name of the policy')
    status: ArkSIARuleStatus = Field(description='Status of the policy')
    description: Optional[str] = Field(default=None, description='Description of the policy')


class ArkSIABasePolicyListItem(ArkSIABasePolicyListItemBase):
    updated_on: str = Field(description='Last update time of the policy')
    rule_names: Optional[List[str]] = Field(default=None, description='Names of the authorization rules of the policy')
