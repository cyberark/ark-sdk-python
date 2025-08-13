from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkCategoryType
from ark_sdk_python.models.services.uap.common.ark_uap_status_type import ArkUAPStatusType


class ArkUAPPoliciesStats(ArkModel):
    policies_count: int = Field(description='Overall count of policies')
    policies_count_per_status: Dict[ArkUAPStatusType, int] = Field(description='Policies count per status')
    policies_count_per_provider: Dict[ArkCategoryType, int] = Field(description='Policies count per target category')
