from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.identity.policies.ark_identity_policy_operation_type import ArkIdentityPolicyOperationType


class ArkIdentityPolicyOperation(ArkModel):
    policy_name: str = Field(description='Policy name')
    operation_type: ArkIdentityPolicyOperationType = Field(description='Operation to perform on the policy')
