from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models.services.uap.common import ArkUAPCommonAccessPolicy
from ark_sdk_python.models.services.uap.sia.common.ark_uap_sia_common_conditions import ArkUAPSIACommonConditions


class ArkUAPSIACommonAccessPolicy(ArkUAPCommonAccessPolicy):
    conditions: Annotated[ArkUAPSIACommonConditions, Field(description='The time, session, and idle time conditions of the policy')]
