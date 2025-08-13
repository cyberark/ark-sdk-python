from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_time_condition import ArkUAPTimeCondition


class ArkUAPConditions(ArkCamelizedModel):
    access_window: ArkUAPTimeCondition = Field(
        description='Indicate the time frame that the policy will be active', default_factory=ArkUAPTimeCondition
    )
    max_session_duration: int = Field(description='Session length', default=1, ge=1, le=24)
