from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_user_data import ArkSIAUserData


class ArkSIABaseAuthorizationRule(ArkCamelizedModel):
    rule_name: str = Field(description='Name of the rule')
    user_data: ArkSIAUserData = Field(description='User data related information of the rule')
