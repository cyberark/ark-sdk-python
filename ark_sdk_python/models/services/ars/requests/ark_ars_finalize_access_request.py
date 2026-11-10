from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkPollableModel
from ark_sdk_python.models.services.ars.requests.ark_ars_access_request import ArkARSAccessRequestResult


class ArkARSFinalizeAccessRequest(ArkPollableModel):
    request_id: str = Field(description='Which request to finalize')
    result: ArkARSAccessRequestResult = Field(description='The finalized result')
    request_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description='Optionally, the request details related to the request that needs to be updated',
    )
    finalization_reason: Optional[str] = Field(default=None, description='If rejected, what is the reason for the rejection')
    wait_until_finished: bool = Field(
        description='If polling is enabled, whether to wait for the entire ' 'request to finish, or only until it reaches pending state',
        default=False,
    )
