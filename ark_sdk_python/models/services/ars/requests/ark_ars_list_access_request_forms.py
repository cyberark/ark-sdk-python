from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.requests.ark_ars_request_type import ArkARSRequestType
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory


class ArkARSListAccessRequestForms(ArkCamelizedModel):
    target_category: ArkTargetCategory = Field(description='Target category to list the access request forms for')
    request_type: ArkARSRequestType = Field(
        description='Request type to list the access request forms for', default=ArkARSRequestType.ON_DEMAND
    )
