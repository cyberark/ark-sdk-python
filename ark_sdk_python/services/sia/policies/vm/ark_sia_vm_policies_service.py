import itertools
import json
from http import HTTPStatus
from typing import Dict, Final, Iterator, List, Set, Tuple, Union

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkPage
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkException, ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.policies.common import (
    ArkSIADeletePolicy,
    ArkSIAGetPolicy,
    ArkSIARuleStatus,
    ArkSIAUpdatePolicyStatus,
)
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policy_list_item import ArkSIABasePolicyListItemBase
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policy_list_item_extanded import ArkSIABasePolicyListItemExtended
from ark_sdk_python.models.services.sia.policies.vm import (
    ArkSIAVMAddPolicy,
    ArkSIAVMPoliciesFilter,
    ArkSIAVMPoliciesStats,
    ArkSIAVMPolicy,
    ArkSIAVMPolicyListItem,
    ArkSIAVMProvidersDict,
    ArkSIAVMUpdatePolicy,
    serialize_sia_vm_policies_protocol_type,
    serialize_sia_vm_policies_workspace_type,
)
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_policies_filter_by_query import (
    POLICIES_QUERY_MAX_LIMIT,
    ArkSIAVMQueryPolicies,
)
from ark_sdk_python.services.ark_service import ArkService

MAX_ITERATIONS: Final[int] = 100

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-policies-vm', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
VM_POLICIES_API: Final[str] = 'api/access-policies'
VM_POLICY_API: Final[str] = 'api/access-policies/{policy_id}'
VM_UPDATE_POLICY_STATUS_API: Final[str] = 'api/access-policies/{policy_id}/status'

ArkPolicyListItemPage = ArkPage[ArkSIABasePolicyListItemBase]


class ArkSIAVMPoliciesService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='dpa',
            refresh_connection_callback=self.__refresh_sia_auth,
        )

    def __refresh_sia_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    @property
    def isp_client(self) -> ArkISPServiceClient:
        return self.__client

    def __policy_id_by_name(self, policy_name: str) -> str:
        policies = list(
            itertools.chain.from_iterable([p.items for p in list(self.list_policies_by(ArkSIAVMPoliciesFilter(name=policy_name)))])
        )

        if not policies:
            raise ArkServiceException(f'Failed to find vm policy id by name [{policy_name}]')
        return policies[0].policy_id

    @staticmethod
    def __serialize_providers_dict(providers_data: ArkSIAVMProvidersDict) -> Dict:
        serialized_providers_data = {}
        for k in list(providers_data.keys()):
            serialized_providers_data[serialize_sia_vm_policies_workspace_type(k)] = providers_data[k].model_dump(by_alias=True)
        return serialized_providers_data

    @staticmethod
    def __serialize_authorization_rules_dict(authorization_rules: List[Dict]) -> None:
        for rule in authorization_rules:
            for k in list(rule['connectionInformation']['connectAs'].keys()):
                for pk in list(rule['connectionInformation']['connectAs'][k].keys()):
                    item = rule['connectionInformation']['connectAs'][k][pk]
                    del rule['connectionInformation']['connectAs'][k][pk]
                    rule['connectionInformation']['connectAs'][k][serialize_sia_vm_policies_protocol_type(pk)] = item
                item = rule['connectionInformation']['connectAs'][k]
                del rule['connectionInformation']['connectAs'][k]
                rule['connectionInformation']['connectAs'][serialize_sia_vm_policies_workspace_type(k)] = item

    def add_policy(self, add_policy: ArkSIAVMAddPolicy) -> ArkSIAVMPolicy:
        """
        Adds a new VM policy with the specified information.

        Args:
            add_policy (ArkDPVMAAddPolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMPolicy: _description_
        """
        self._logger.info(f'Adding new vm policy [{add_policy.policy_name}]')
        add_policy_dict = add_policy.model_dump(by_alias=True)
        add_policy_dict['providersData'] = self.__serialize_providers_dict(add_policy.providers_data)
        self.__serialize_authorization_rules_dict(add_policy_dict['userAccessRules'])
        resp: Response = self.__client.post(VM_POLICIES_API, json=add_policy_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                policy_id = resp.json()['policyId']
                return self.policy(ArkSIAGetPolicy(policy_id=policy_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add vm policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add vm policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add vm policy [{resp.text}] - [{resp.status_code}]')

    def delete_policy(self, delete_policy: ArkSIADeletePolicy) -> None:
        """
        Deletes the specified (ID or name) VM policy.

        Args:
            delete_policy (ArkSIADeletePolicy): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_policy.policy_name and not delete_policy.policy_id:
            delete_policy.policy_id = self.__policy_id_by_name(delete_policy.policy_name)
        self._logger.info(f'Deleting vm policy [{delete_policy.policy_id}]')
        resp: Response = self.__client.delete(VM_POLICY_API.format(policy_id=delete_policy.policy_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete vm policy [{resp.text}] - [{resp.status_code}]')

    def update_policy(self, update_policy: ArkSIAVMUpdatePolicy) -> ArkSIAVMPolicy:
        """
        Updates a VM policy.

        Args:
            update_policy (ArkSIAVMUpdatePolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMPolicy: _description_
        """
        if update_policy.policy_name and not update_policy.policy_id:
            update_policy.policy_id = self.__policy_id_by_name(update_policy.policy_name)
        self._logger.info(f'Updating vm policy [{update_policy.policy_id}]')
        update_dict = json.loads(
            update_policy.model_dump_json(by_alias=True, exclude_none=True, exclude={'new_policy_name', 'policy_name'})
        )
        if update_policy.new_policy_name:
            update_dict['policyName'] = update_policy.new_policy_name
        else:
            update_dict['policyName'] = update_policy.policy_name
        if update_policy.providers_data:
            update_dict['providersData'] = self.__serialize_providers_dict(update_policy.providers_data)
        if 'userAccessRules' in update_dict:
            self.__serialize_authorization_rules_dict(update_dict['userAccessRules'])
        resp: Response = self.__client.put(VM_POLICY_API.format(policy_id=update_policy.policy_id), json=update_dict)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIAVMPolicy.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update vm policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update vm policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update vm policy [{resp.text}] - [{resp.status_code}]')

    def update_policy_status(self, update_policy_status: ArkSIAUpdatePolicyStatus) -> ArkSIAVMPolicy:
        """
        Updates the status of the specified (by ID) VM policy.

        Args:
            update_policy_status (ArkSIAUpdatePolicyStatus): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMPolicy: _description_
        """
        if update_policy_status.policy_name and not update_policy_status.policy_id:
            update_policy_status.policy_id = self.__policy_id_by_name(update_policy_status.policy_name)
        self._logger.info(f'Updating vm policy status [{update_policy_status.policy_id}]')
        resp: Response = self.__client.put(
            VM_UPDATE_POLICY_STATUS_API.format(policy_id=update_policy_status.policy_id),
            json=update_policy_status.model_dump(exclude={'policy_id'}),
        )
        if resp.status_code == HTTPStatus.OK:
            return self.policy(ArkSIAGetPolicy(policy_id=update_policy_status.policy_id))
        raise ArkServiceException(f'Failed to update vm policy status [{resp.text}] - [{resp.status_code}]')

    def __get_policies(self, params: dict) -> Tuple[List[Union[ArkSIABasePolicyListItemExtended, ArkSIAVMPolicyListItem]], int]:
        resp: Response = self.__client.get(VM_POLICIES_API, params=params)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to list vm policies [{resp.text}] - [{resp.status_code}]')
        try:
            return self.__parse_policies(resp, params.get('extended', False)), json.loads(resp.text)['totalCount']
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse list vm policies response [{str(ex)}] - [{resp.text}]')
            raise ArkServiceException(f'Failed to parse list vm policies response [{str(ex)}]') from ex

    def query_policies(self, policies_filter: ArkSIAVMQueryPolicies = None) -> Iterator[ArkPolicyListItemPage]:
        """
        Lists VM policies that match the specified query.

        Raises:
            ArkServiceException: _description_

        Returns:
            Iterator[ArkPolicyListItemPage]: _description_
        """
        if policies_filter is not None and not isinstance(policies_filter, ArkSIAVMQueryPolicies):
            raise TypeError('policies_filter must be an instance of ArkSIAVMPoliciesFilterByQuery')

        self._logger.info(f'Retrieving all vm policies that comply to the filter: {policies_filter=}')
        params = self.__build_url_params(policies_filter=policies_filter)
        offset = params.get('offset', 0)

        iteration_count = 0
        while True:
            params['offset'] = offset
            parsed_policies, total_policies = self.__get_policies(params=params)
            yield ArkPolicyListItemPage(items=parsed_policies)

            offset += len(parsed_policies)
            if offset >= total_policies or (policies_filter and policies_filter.limit):
                break

            iteration_count += 1
            if iteration_count >= MAX_ITERATIONS:
                raise ArkException('Reached maximum number of iterations for listing policies.')

    def __build_url_params(self, policies_filter: ArkSIAVMQueryPolicies = None) -> Dict:
        if not policies_filter:
            return {}

        query_params = {}
        if policies_filter.filter_string:
            query_params['filter'] = policies_filter.filter_string
        if policies_filter.limit:
            query_params['limit'] = policies_filter.limit
        else:
            query_params['limit'] = POLICIES_QUERY_MAX_LIMIT
        if policies_filter.extended:
            query_params['extended'] = policies_filter.extended
        if policies_filter.sort:
            query_params['sort'] = policies_filter.sort
        if policies_filter.offset:
            query_params['offset'] = policies_filter.offset
        return query_params

    def __parse_policies(
        self, response: Response, is_extended: bool
    ) -> List[Union[ArkSIABasePolicyListItemExtended, ArkSIAVMPolicyListItem]]:
        response_items = response.json()['items']
        if is_extended:
            for item in response_items:
                # Inserting the provider name into the provider data for parsing reasons
                if 'providersData' in item:
                    for provider, provider_data in item['providersData'].items():
                        provider_data['provider_name'] = provider
        return TypeAdapter(List[ArkSIABasePolicyListItemExtended if is_extended else ArkSIAVMPolicyListItem]).validate_python(
            response_items
        )

    def list_policies(self) -> Iterator[ArkPolicyListItemPage]:
        """
        Lists all the tenants' VM policies.

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkSIAVMPolicyListItem]: _description_
        """
        return self.query_policies()

    def list_policies_by(self, policies_filter: ArkSIAVMPoliciesFilter) -> Iterator[ArkPolicyListItemPage]:
        """
        Lists VM policies that match the specified filters.

        Args:
            policies_filter (ArkSIAVMPoliciesFilter): _description_

        Returns:
            Iterator[ArkPolicyListItemPage]: _description_
        """
        self._logger.info(f'Retrieving vm policies by filter [{policies_filter}]')
        filter_pairs = []

        # Filter by statuses
        if policies_filter.statuses:
            filter_pairs = [('status', status.value, 'eq') for status in policies_filter.statuses]

        # Filter by name wildcard
        if policies_filter.name:
            filter_pairs.append(('policyName', policies_filter.name, 'eq'))

        # Filter by cloud providers
        if policies_filter.providers:
            platform_pairs = [('platforms', platform.upper(), 'contains') for platform in policies_filter.providers]
            filter_pairs.extend(platform_pairs)

        final_filter = self.__build_filter_string(filter_pairs)
        return self.query_policies(ArkSIAVMQueryPolicies(filter_string=final_filter))

    def __build_filter_string(self, filter_pairs):
        final_filter = ""
        for index in range(len(filter_pairs)):
            if index == 0:
                final_filter = f"({filter_pairs[index][0]} {filter_pairs[index][2]} '{filter_pairs[index][1]}')"
            else:
                if filter_pairs[index][0] == 'status':
                    final_filter = f"({final_filter} or ({filter_pairs[index][0]} {filter_pairs[index][2]} '{filter_pairs[index][1]}'))"
                else:
                    final_filter = f"({final_filter} and ({filter_pairs[index][0]} {filter_pairs[index][2]} '{filter_pairs[index][1]}'))"
        return final_filter

    def policy(self, get_policy: ArkSIAGetPolicy) -> ArkSIAVMPolicy:
        """
        Retrieves a VM policy by ID.

        Args:
            get_policy (ArkSIAGetPolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMPolicy: _description_
        """
        if get_policy.policy_name and not get_policy.policy_id:
            get_policy.policy_id = self.__policy_id_by_name(get_policy.policy_name)
        self._logger.info(f'Retrieving vm policy [{get_policy.policy_id}]')
        resp: Response = self.__client.get(VM_POLICY_API.format(policy_id=get_policy.policy_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIAVMPolicy.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse vm policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse vm policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve vm policy [{get_policy.policy_id}] [{resp.text}] - [{resp.status_code}]')

    def policies_stats(self) -> ArkSIAVMPoliciesStats:
        """
        Calculates VM policy statistics.

        Returns:
            ArkSIAVMPoliciesStats: _description_
        """
        self._logger.info('Calculating vm policies stats')
        policies = list(itertools.chain.from_iterable([p.items for p in list(self.list_policies())]))
        policies_stats = ArkSIAVMPoliciesStats.model_construct()
        policies_stats.policies_count = len(policies)

        # Count policies per status
        status_types: Set[ArkSIARuleStatus] = {p.status for p in policies if p.status}
        policies_stats.policies_count_per_status = {st: len([p for p in policies if p.status and p.status == st]) for st in status_types}

        # Count policies per platforms
        policies_stats.policies_count_per_provider = {}
        for policy in policies:
            for platform in policy.platforms:
                if platform not in policies_stats.policies_count_per_provider:
                    policies_stats.policies_count_per_provider[platform] = 0
                policies_stats.policies_count_per_provider[platform] += 1

        return policies_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
