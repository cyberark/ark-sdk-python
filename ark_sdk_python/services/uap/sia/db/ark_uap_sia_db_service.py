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
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_access_policy import ArkUAPSIADBAccessPolicy
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_filters import ArkUAPSIADBFilters
from ark_sdk_python.services.uap.common import ArkUAPBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='uap-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)


class ArkUAPSIADBService(ArkUAPBaseService):
    def add_policy(self, add_policy: ArkUAPSIADBAccessPolicy) -> ArkUAPSIADBAccessPolicy:
        """
        Adds a new SIA DB policy with the given information.

        Args:
            add_policy (ArkUAPSIADBAccessPolicy): The policy to be added.

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

    def policy(self, policy_request: ArkUAPGetPolicyRequest) -> ArkUAPSIADBAccessPolicy:
        """
        Gets a SIA DB policy by id.

        Args:
            policy_request (ArkUAPGetPolicyRequest): _description_

        Raises:
            ArkServiceException: _description_


        Returns:
            ArkUAPSIADBAccessPolicy: the request policy.
        """
        return ArkUAPSIADBAccessPolicy(**self._base_policy(policy_request=policy_request))

    def update_policy(self, update_policy: ArkUAPSIADBAccessPolicy) -> ArkUAPSIADBAccessPolicy:
        """
        Edits an existing SIA DB policy with the given information.

        Args:
            update_policy (ArkUAPSIADBAccessPolicy): The policy to be edited.

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
         Retrieves all SIA DB policies.

        Raises:
         ArkServiceException: If failed to get all policies.

         Returns:
             ArkUAPPolicyResultsResponse: The response containing all SIA DB policies.
        """
        return self._base_list_policies(ArkUAPFilters(target_category=[ArkCategoryType.DB]))

    def list_policies_by(self, policies_filter: ArkUAPSIADBFilters) -> ArkUAPPolicyResultsResponse:
        """
        Retrieves SIA DB policies based on the provided filters.

        Args:
            policies_filter (ArkUAPSIADBFilters): The filters to apply when retrieving policies.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPolicyResultsResponse: The response containing the filtered policies.
        """
        return self._base_list_policies(ark_uap_filter=policies_filter)

    def policies_stats(self) -> ArkUAPPoliciesStats:
        """
        Calculates SIA DB policies statistics

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPoliciesStats: Summary of SIA DB policies by status and provider.
        """
        return self._base_policies_stats(ArkUAPFilters(target_category=[ArkCategoryType.DB]))

    @staticmethod
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
