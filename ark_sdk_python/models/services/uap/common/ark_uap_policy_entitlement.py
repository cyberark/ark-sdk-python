from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkCategoryType, ArkWorkspaceType
from ark_sdk_python.models.services.uap.common.ark_uap_policy_type import ArkUAPPolicyType
from ark_sdk_python.models.services.uap.utils.ark_uap_policies_workspace_type_serializer import serialize_uap_policies_workspace_type


class ArkUAPPolicyEntitlement(ArkCamelizedModel):
    target_category: ArkCategoryType = Field(description='The target category of the policy')
    location_type: ArkWorkspaceType = Field(description='The location type of the policy')
    policy_type: ArkUAPPolicyType = Field(description='Policy type', default=ArkUAPPolicyType.RECURRING)

    def model_dump(self, **kwargs) -> dict:
        data = super().model_dump(**kwargs)
        data['locationType'] = serialize_uap_policies_workspace_type(self.location_type)
        return data
