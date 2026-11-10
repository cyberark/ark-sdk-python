from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.requests.ark_ars_request_type import ArkARSRequestType
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory


class ArkARSGetAccessRequestSurvey(ArkCamelizedModel):
    target_category: ArkTargetCategory = Field(description='Target category of the survey that is required')
    request_type: ArkARSRequestType = Field(description='The type of request', default=ArkARSRequestType.ON_DEMAND)
