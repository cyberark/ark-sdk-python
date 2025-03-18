from typing import Optional

from pydantic import Field

from ark_sdk_python.models.services.sia.policies.common import ArkSIABaseAuthorizationRule
from ark_sdk_python.models.services.sia.policies.vm import ArkSIAVMConnectionInformation


class ArkSIABaseAuthorizationRuleExtended(ArkSIABaseAuthorizationRule):
    connection_information: Optional[ArkSIAVMConnectionInformation] = Field(
        default=None, description='Connection information of the policy'
    )
