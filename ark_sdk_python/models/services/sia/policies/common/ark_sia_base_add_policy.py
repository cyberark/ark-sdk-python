from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_rule_status import ArkSIARuleStatus


class ArkSIABaseAddPolicy(ArkCamelizedModel):
    policy_name: Optional[str] = Field(default=None, description='Policy name to be added')
    description: Optional[str] = Field(default=None, description='Description about the policy to add')
    status: ArkSIARuleStatus = Field(description='Status of the policy upon adding', default=ArkSIARuleStatus.Draft)
    start_date: Optional[str] = Field(
        default=None, description='When will the policy start taking effect, empty means it will take effect when added'
    )
    end_date: Optional[str] = Field(
        default=None, description='When will the policy stop taking effect, empty means it will never stop taking effect'
    )
