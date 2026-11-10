from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkPollableModel
from ark_sdk_python.models.services.ars.requests.ark_ars_request_type import ArkARSRequestType
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory


class ArkARSSubmitAccessRequest(ArkPollableModel):
    target_category: ArkTargetCategory = Field(description='What is the category that is required to execute')
    request_type: ArkARSRequestType = Field(description='The type of request to start', default=ArkARSRequestType.ON_DEMAND)
    request_details: Dict[str, Any] = Field(description='The details related to the workload', default=None)
    association: Optional[Dict[str, Any]] = Field(description='Optionally an associated policy', default=None)
    wait_until_finished: bool = Field(
        description='If polling is enabled, whether to wait for the entire request to finish, or only until it reaches pending state',
        default=False,
    )
