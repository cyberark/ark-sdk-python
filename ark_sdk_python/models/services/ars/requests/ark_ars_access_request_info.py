from datetime import datetime
from typing import List, Optional, Union

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.requests.ark_ars_access_request import ArkARSAccessRequest, ArkARSAccessRequestState
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory


class ArkARSAccessRequestInfo(ArkCamelizedModel):
    request_id: str = Field(description='ID of the request')
    request_rule: Optional[str] = Field(description='ID of the rule being used for the request', default=None)
    target_category: ArkTargetCategory = Field(description='Target category the request is related to')
    request_link: Optional[str] = Field(description='Link to the request itself', default=None)
    request_state: ArkARSAccessRequestState = Field(description='Current request state')
    creation_time: datetime = Field(description='Creation time of the request')
    last_update_time: datetime = Field(description='When was the request last updated')


class ArkARSAccessRequestsInfo(ArkCamelizedModel):
    items: List[Union[ArkARSAccessRequestInfo, ArkARSAccessRequest]] = Field(description='Amount of items')
    count: int = Field(description='Count of items returned post filter / pagination')
    total_count: int = Field(description='Overall items that exists')
