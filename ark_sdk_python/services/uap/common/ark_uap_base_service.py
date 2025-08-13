# pylint: disable=unused-private-member
from abc import ABC, abstractmethod
from collections import defaultdict
from http import HTTPStatus
from typing import Any, Dict, Final, List, Optional

from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.uap.common import ArkUAPGetPolicyRequest, ArkUAPGetPolicyStatus, ArkUAPStatusType
from ark_sdk_python.models.services.uap.common.ark_uap_common_access_policy import ArkUAPCommonAccessPolicy
from ark_sdk_python.models.services.uap.common.ark_uap_delete_policy_request import ArkUAPDeletePolicyRequest
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_request import ArkUAPFilters, ArkUAPGetAccessPoliciesRequest
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_response import ArkUAPPolicyResultsResponse
from ark_sdk_python.models.services.uap.common.ark_uap_get_policy_by_name_request import ArkUAPGetPolicyByNameRequest
from ark_sdk_python.models.services.uap.common.ark_uap_policies_stats import ArkUAPPoliciesStats
from ark_sdk_python.models.services.uap.common.ark_uap_response import ArkUAPResponse
from ark_sdk_python.services.ark_service import ArkService

POLICIES_API: Final[str] = 'api/policies'
POLICY_API: Final[str] = 'api/policies/{policy_id}'


class ArkUAPBaseService(ArkService, ABC):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self._client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='uap',
            refresh_connection_callback=self.__refresh_uap_auth,
        )

    def __refresh_uap_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    def _base_add_policy(self, add_policy: Dict[str, Any], policy_name: str) -> ArkUAPResponse:
        """
        Adds a new policy with the given information

        Args:
            add_policy (Dict[str, Any]): _description_
            policy_name (str): The name of the policy to be added.

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPResponse: _description_
        """
        self._logger.info(f'Adding new policy [{policy_name}]')
        resp: Response = self._client.post(POLICIES_API, json=add_policy)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkUAPResponse.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add policy [{resp.text}] - [{resp.status_code}]')

    def _base_policy(self, policy_request: ArkUAPGetPolicyRequest) -> Dict[str, Any]:
        self._logger.info(f'get policy [{policy_request.policy_id}]')
        resp: Response = self._client.get(POLICY_API.format(policy_id=policy_request.policy_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to get policy [{resp.text}] - [{resp.status_code}]')
        return resp.json()

    def delete_policy(self, delete_policy: ArkUAPDeletePolicyRequest) -> None:
        """
        Deletes a policy by id

        Args:
            delete_policy (ArkUAPDeletePolicyRequest): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting policy [{delete_policy.policy_id}]')
        resp: Response = self._client.delete(POLICY_API.format(policy_id=delete_policy.policy_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to delete policy [{resp.text}] - [{resp.status_code}]')

    def policy_status(self, get_policy_status: ArkUAPGetPolicyStatus) -> ArkUAPStatusType:
        """
        Retrieves a policy status by its id or name

        Args:
            get_policy_status (ArkSCAGetPolicyStatus): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkUAPStatusType: _description_
        """

        self._logger.info('Retrieving policy status')
        if get_policy_status.policy_id:
            return ArkUAPCommonAccessPolicy(
                **self._base_policy(ArkUAPGetPolicyRequest(policy_id=get_policy_status.policy_id))
            ).metadata.status.status
        if get_policy_status.policy_name:
            return self._base_policy_by_name(ArkUAPGetPolicyByNameRequest(policy_name=get_policy_status.policy_name)).metadata.status.status
        raise ArkServiceException('Failed to retrieve policy status')

    def _base_update_policy(self, update_policy: Dict[str, Any], policy_id: str) -> None:
        """
        Updates a policy with new information

        Args:
            update_policy (Dict[str, Any]): _description_
            policy_id (str): The id of the policy to update.

        Raises:
            ArkServiceException: _description_

        Returns:
            None
        """

        self._logger.info(f'Updating policy [{policy_id}]')
        resp: Response = self._client.put(POLICY_API.format(policy_id=policy_id), json=update_policy)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to update policy [{resp.text}] - [{resp.status_code}]')

    def _base_list_policies(self, ark_uap_filter: Optional[ArkUAPFilters] = None) -> ArkUAPPolicyResultsResponse:
        """
        Retrieves all policies of the tenant.

        Args:
            ark_uap_filter (Optional[ark_uap_filter]):

        Raises:
            ArkServiceException: If failed to get all policies.

        Returns:
            ArkUAPPolicyResultsResponse: Aggregated response of all policies.
        """
        self._logger.info('Retrieving policies')

        filters = ark_uap_filter if ark_uap_filter else ArkUAPFilters()
        next_token = None
        prev_token = None
        aggregated_results: List[ArkUAPCommonAccessPolicy] = []

        page_count = 0

        try:
            while True:
                if page_count > filters.max_pages:
                    break  # Stop if we exceed the maximum number of pages

                page_count += 1

                params = ArkUAPGetAccessPoliciesRequest(filters=filters, next_token=next_token).build_get_query_params()

                resp: Response = self._client.get(POLICIES_API, params=params.model_dump(by_alias=True))

                if resp.status_code != HTTPStatus.OK:
                    raise ArkServiceException(f'Failed to get all policies [{resp.text}] - [{resp.status_code}]')

                result = ArkUAPPolicyResultsResponse.model_validate(resp.json())
                aggregated_results.extend(result.results)

                prev_token, next_token = next_token, result.next_token

                if not next_token:
                    break
                if next_token == prev_token:
                    self._logger.error('Pagination stuck: next_token did not change between requests')
                    raise ArkServiceException('Pagination loop detected: stuck on same next_token')

            return ArkUAPPolicyResultsResponse(results=aggregated_results, next_token=None, total=len(aggregated_results))

        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse get all policies response [{str(ex)}] - [{resp.text}]')
            raise ArkServiceException(f'Failed to parse get all policies response [{str(ex)}]') from ex

    def _base_policies_stats(self, ark_uap_filter: Optional[ArkUAPFilters] = None) -> ArkUAPPoliciesStats:
        """
        Calculates policies statistics

         Args:
            ark_uap_filter (Optional[ark_uap_filter]):

        Returns:
            ArkUAPPoliciesStats: Summary of policies by status and provider.
        """
        self._logger.info('Calculating policies stats')
        policies = self._base_list_policies(ark_uap_filter=ark_uap_filter).results

        policies_stats = ArkUAPPoliciesStats.model_construct()
        policies_stats.policies_count = len(policies)

        status_counts = defaultdict(int)
        provider_counts = defaultdict(int)

        for policy in policies:
            status_counts[policy.metadata.status.status] += 1
            provider_counts[policy.metadata.policy_entitlement.location_type] += 1

        policies_stats.policies_count_per_status = dict(status_counts)
        policies_stats.policies_count_per_provider = dict(provider_counts)

        return policies_stats

    def _base_policy_by_name(self, policy_request: ArkUAPGetPolicyByNameRequest) -> ArkUAPCommonAccessPolicy:
        """
        get a  ccommon policy by the name

        Args:
            policy_request (ArkUAPGetPolicyByNameRequest): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'get policy by name [{policy_request.policy_name}]')
        result = self._base_list_policies(ArkUAPFilters(text_search=policy_request.policy_name)).results
        if result:
            for policy in result:
                if policy.metadata.name == policy_request.policy_name:
                    return ArkUAPCommonAccessPolicy(**policy.model_dump(by_alias=True))
        raise ArkServiceException(f'Failed to get policy by name [{policy_request.policy_name}]')

    @staticmethod
    @abstractmethod
    def service_config() -> ArkServiceConfig:
        """
        Returns the service configuration, which includes the service name, and its required and optional authenticators.

        Returns:
            ArkServiceConfig: _description_
        """
