from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_user_data import ArkDPAUserData


class ArkDPABaseAuthorizationRule(ArkCamelizedModel):
    rule_name: str = Field(description='Name of the rule')
    user_data: ArkDPAUserData = Field(description='User data related information of the rule')
