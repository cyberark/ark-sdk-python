from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_rule_status import ArkSIARuleStatus


class ArkSIABasePoliciesFilter(ArkModel):
    statuses: Optional[List[ArkSIARuleStatus]] = Field(default=None, description='Filter policies by given rule statuses')
    name: Optional[str] = Field(default=None, description='Filter by policy name wildcard')
