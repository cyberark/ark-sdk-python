from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_rule_status import ArkDPARuleStatus


class ArkDPABaseAddPolicy(ArkCamelizedModel):
    policy_name: str = Field(description='Policy name to be added')
    description: Optional[str] = Field(description='Description about the policy to add')
    status: ArkDPARuleStatus = Field(description='Status of the policy upon adding', default=ArkDPARuleStatus.Draft)
    start_date: Optional[str] = Field(description='When will the policy start taking effect, empty means it will take effect when added')
    end_date: Optional[str] = Field(description='When will the policy stop taking effect, empty means it will never stop taking effect')
