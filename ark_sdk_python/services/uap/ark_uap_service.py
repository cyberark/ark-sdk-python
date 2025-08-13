from typing import Final

from overrides import overrides

from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_request import ArkUAPFilters
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_response import ArkUAPPolicyResultsResponse
from ark_sdk_python.models.services.uap.common.ark_uap_policies_stats import ArkUAPPoliciesStats
from ark_sdk_python.services.uap.common.ark_uap_base_service import ArkUAPBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='uap', required_authenticator_names=['isp'], optional_authenticator_names=[]
)


class ArkUAPService(ArkUAPBaseService):

    def list_policies(self) -> ArkUAPPolicyResultsResponse:
        """
         Retrieves all policies.

        Raises:
         ArkServiceException: If failed to get all policies.

         Returns:
             ArkUAPPolicyResultsResponse: The response containing all policies.
        """
        return self._base_list_policies(ArkUAPFilters())

    def policies_stats(self) -> ArkUAPPoliciesStats:
        """
        Calculates policies statistics

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPPoliciesStats: Summary of policies by status and provider.
        """
        return self._base_policies_stats(ArkUAPFilters())

    def list_policies_by(self, policies_filter: ArkUAPFilters) -> ArkUAPPolicyResultsResponse:
        """
        Retrieves policies based on the provided filters.

        Args:
            policies_filter (ArkUAPFilters): The filters to apply when retrieving policies.

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
