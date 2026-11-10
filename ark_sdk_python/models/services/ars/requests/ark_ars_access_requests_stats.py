from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.requests.ark_ars_access_request import (
    ArkARSAccessRequestResult,
    ArkARSAccessRequestState,
    ArkTargetCategory,
)


class ArkARSAccessRequestsStats(ArkCamelizedModel):
    requests_count: int = Field(description='Overall access requests count')
    requests_count_by_category: Dict[ArkTargetCategory, int] = Field(description='Access requests count by category')
    requests_count_by_state: Dict[ArkARSAccessRequestState, int] = Field(description='Access requests count by state')
    requests_count_by_result: Dict[ArkARSAccessRequestResult, int] = Field(description='Access requests count by result')
