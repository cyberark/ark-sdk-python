from typing import Final

from overrides import overrides

from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import ArkCategoryType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.uap.common import ArkUAPStatusType
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_request import ArkUAPFilters
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_response import ArkUAPPolicyResultsResponse
from ark_sdk_python.models.services.uap.common.ark_uap_get_policy_request import ArkUAPGetPolicyRequest
from ark_sdk_python.models.services.uap.common.ark_uap_policies_stats import ArkUAPPoliciesStats
from ark_sdk_python.models.services.uap.common.ark_uap_response import ArkUAPResponse
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_cloud_console_access_policy import ArkUAPSCACloudConsoleAccessPolicy
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_filters import ArkUAPSCAFilters
from ark_sdk_python.services.uap.common.ark_uap_base_service import ArkUAPBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='uap-sca', required_authenticator_names=['isp'], optional_authenticator_names=[]
)


class ArkUAPSCAService(ArkUAPBaseService):

    __MAX_ACTIVE_STATUS_RETRY_COUNT: Final[int] = 10

    def add_policy(self, add_policy: ArkUAPSCACloudConsoleAccessPolicy) -> ArkUAPSCACloudConsoleAccessPolicy:
        """
        Adds a new policy with the given information

        Args:
            add_policy (ArkUAPSCACloudConsoleAccessPolicy): The policy to be added.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPResponse: _description_
        """
        add_policy_response: ArkUAPResponse = self._base_add_policy(
            add_policy.serialize_model(by_alias=True, exclude_none=True),
            policy_name=add_policy.metadata.name,
        )
        retry_count = 0
        while True:
            policy = self.policy(ArkUAPGetPolicyRequest(policy_id=add_policy_response.policy_id))
            if policy.metadata.status == ArkUAPStatusType.ACTIVE:
                break
            if policy.metadata.status == ArkUAPStatusType.ERROR:
                raise ArkServiceException(f'Policy [{add_policy_response.policy_id}] is in error state')
            if retry_count >= ArkUAPSCAService.__MAX_ACTIVE_STATUS_RETRY_COUNT:
                self._logger.warning(
                    f'Policy [{add_policy_response.policy_id}] is not active after 10 retries, '
                    f'might indicate an issue, moving on regardless'
                )
                break
            retry_count += 1
        return self.policy(ArkUAPGetPolicyRequest(policy_id=add_policy_response.policy_id))

    def policy(self, policy_request: ArkUAPGetPolicyRequest) -> ArkUAPSCACloudConsoleAccessPolicy:
        """
        get a policy by id

        Args:
            policy_request (ArkUAPGetPolicyRequest): _description_

        Raises:
            ArkServiceException: _description_


        Returns:
            ArkUAPSCACloudConsoleAccessPolicy: the request policy.
        """
        return ArkUAPSCACloudConsoleAccessPolicy.deserialize_model(self._base_policy(policy_request=policy_request))

    def update_policy(self, update_policy: ArkUAPSCACloudConsoleAccessPolicy) -> ArkUAPSCACloudConsoleAccessPolicy:
        """
        Edits an existing policy with the given information.

        Args:
            update_policy (ArkUAPSCACloudConsoleAccessPolicy): The policy to be edited.

        Raises:
            ArkServiceException: _description_

        """
        self._base_update_policy(
            update_policy=update_policy.serialize_model(by_alias=True, exclude_none=True),
            policy_id=update_policy.metadata.policy_id,
        )
        retry_count = 0
        while True:
            policy = self.policy(ArkUAPGetPolicyRequest(policy_id=update_policy.metadata.policy_id))
            if policy.metadata.status == ArkUAPStatusType.ACTIVE:
                break
            if policy.metadata.status == ArkUAPStatusType.ERROR:
                raise ArkServiceException(f'Policy [{update_policy.metadata.policy_id}] is in error state')
            if retry_count >= ArkUAPSCAService.__MAX_ACTIVE_STATUS_RETRY_COUNT:
                self._logger.warning(
                    f'Policy [{update_policy.metadata.policy_id}] is not active after 10 retries, '
                    f'might indicate an issue, moving on regardless'
                )
                break
            retry_count += 1
        return self.policy(ArkUAPGetPolicyRequest(policy_id=update_policy.metadata.policy_id))

    def list_policies(self) -> ArkUAPPolicyResultsResponse:
        """
         Retrieves all policies.

        Raises:
         ArkServiceException: If failed to get all policies.

         Returns:
             ArkUAPPolicyResultsResponse: The response containing all policies.
        """
        return self._base_list_policies(ArkUAPFilters(target_category=[ArkCategoryType.CLOUD_CONSOLE]))

    def policies_stats(self) -> ArkUAPPoliciesStats:
        """
        Calculates policies statistics

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPoliciesStats: Summary of policies by status and provider.
        """
        return self._base_policies_stats(ArkUAPFilters(target_category=[ArkCategoryType.CLOUD_CONSOLE]))

    def list_policies_by(self, policies_filter: ArkUAPSCAFilters) -> ArkUAPPolicyResultsResponse:
        """
        Retrieves policies based on the provided filters.

        Args:
            policies_filter (ArkUAPSCAFilters): The filters to apply when retrieving policies.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPolicyResultsResponse: The response containing the filtered policies.
        """
        return self._base_list_policies(policies_filter)

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
