from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_rule_status import ArkDPARuleStatus


class ArkDPABasePoliciesFilter(ArkModel):
    statuses: Optional[List[ArkDPARuleStatus]] = Field(description='Filter policies by given rule statuses')
    name: Optional[str] = Field(description='Filter by policy name wildcard')
