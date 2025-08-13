from typing import Final

from ark_sdk_python.models.common import ArkCategoryType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.uap.common import (
    ArkUAPFilters,
    ArkUAPGetPolicyRequest,
    ArkUAPPoliciesStats,
    ArkUAPPolicyResultsResponse,
    ArkUAPResponse,
)
from ark_sdk_python.models.services.uap.sia.vm import ArkUAPSIAVMFilters
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_access_policy import ArkUAPSIAVMAccessPolicy
from ark_sdk_python.services.uap.common import ArkUAPBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='uap-vm', required_authenticator_names=['isp'], optional_authenticator_names=[]
)


class ArkUAPSIAVMService(ArkUAPBaseService):
    def add_policy(self, add_policy: ArkUAPSIAVMAccessPolicy) -> ArkUAPSIAVMAccessPolicy:
        """
        Adds a new SIA VM policy with the given information.

        Args:
            add_policy (ArkUAPSIAVMAccessPolicy): The policy to be added.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPResponse: _description_
        """
        add_policy_response: ArkUAPResponse = self._base_add_policy(
            add_policy=add_policy.serialize_model(by_alias=True, exclude_none=True),
            policy_name=add_policy.metadata.name,
        )
        return self.policy(ArkUAPGetPolicyRequest(policy_id=add_policy_response.policy_id))

    def policy(self, policy_request: ArkUAPGetPolicyRequest) -> ArkUAPSIAVMAccessPolicy:
        """
        Gets a SIA VM policy by id.

        Args:
            policy_request (ArkUAPGetPolicyRequest): _description_

        Raises:
            ArkServiceException: _description_


        Returns:
            ArkUAPSIAVMAccessPolicy: the request policy.
        """
        return ArkUAPSIAVMAccessPolicy.deserialize_model(self._base_policy(policy_request=policy_request))

    def update_policy(self, update_policy: ArkUAPSIAVMAccessPolicy) -> ArkUAPSIAVMAccessPolicy:
        """
        Edits an existing SIA VM policy with the given information.

        Args:
            update_policy (ArkUAPSIAVMAccessPolicy): The policy to be edited.

        Raises:
            ArkServiceException: _description_

        """
        self._base_update_policy(
            update_policy=update_policy.serialize_model(by_alias=True, exclude_none=True),
            policy_id=update_policy.metadata.policy_id,
        )

        return self.policy(ArkUAPGetPolicyRequest(policy_id=update_policy.metadata.policy_id))

    def list_policies(self) -> ArkUAPPolicyResultsResponse:
        """
         Retrieves all SIA VM policies.

        Raises:
         ArkServiceException: If failed to get all policies.

         Returns:
             ArkUAPPolicyResultsResponse: The response containing all SIA VM policies.
        """
        return self._base_list_policies(ArkUAPFilters(target_category=[ArkCategoryType.VM]))

    def list_policies_by(self, policies_filter: ArkUAPSIAVMFilters) -> ArkUAPPolicyResultsResponse:
        """
        Retrieves SIA VM policies based on the provided filters.

        Args:
            policies_filter (ArkUAPSIAVMFilters): The filters to apply when retrieving policies.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPolicyResultsResponse: The response containing the filtered policies.
        """
        return self._base_list_policies(ark_uap_filter=policies_filter)

    def policies_stats(self) -> ArkUAPPoliciesStats:
        """
        Calculates SIA VM policies statistics

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPoliciesStats: Summary of SIA VM policies by status and provider.
        """
        return self._base_policies_stats(ArkUAPSIAVMFilters(target_category=[ArkCategoryType.VM]))

    @staticmethod
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
