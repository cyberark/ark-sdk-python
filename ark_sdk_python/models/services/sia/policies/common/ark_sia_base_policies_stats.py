from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_rule_status import ArkSIARuleStatus


class ArkSIABasePoliciesStats(ArkModel):
    policies_count: int = Field(description='Overall count of policies')
    policies_count_per_status: Dict[ArkSIARuleStatus, int] = Field(description='Policies count per rule status')
