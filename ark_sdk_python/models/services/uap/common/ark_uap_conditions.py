from typing import Optional

from pydantic import Field, model_serializer

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_access_approval import ArkUAPAccessApproval
from ark_sdk_python.models.services.uap.common.ark_uap_time_condition import ArkUAPTimeCondition


class ArkUAPConditions(ArkCamelizedModel):
    access_window: ArkUAPTimeCondition = Field(
        description='Indicate the time frame that the policy will be active', default_factory=ArkUAPTimeCondition
    )
    max_session_duration: int = Field(description='Session length', default=1, ge=1, le=24)
    access_approval: Optional[ArkUAPAccessApproval] = Field(
        default=None,
        description='Optional dual-control access approval requirements when supported by the policy type',
    )

    @model_serializer(mode='wrap')
    def serialize_model(self, handler) -> dict:
        data = handler(self)
        if isinstance(data, dict) and data.get('accessApproval') is None:
            data.pop('accessApproval', None)
        return data
