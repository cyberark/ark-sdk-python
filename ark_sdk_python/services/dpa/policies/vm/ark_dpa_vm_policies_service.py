import json
from fnmatch import fnmatch
from http import HTTPStatus
from typing import Dict, Final, List, Set

from overrides import overrides
from pydantic import parse_obj_as
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.policies.common import (
    ArkDPADeletePolicy,
    ArkDPAGetPolicy,
    ArkDPARuleStatus,
    ArkDPAUpdatePolicyStatus,
)
from ark_sdk_python.models.services.dpa.policies.vm import (
    ArkDPAVMAddPolicy,
    ArkDPAVMPoliciesFilter,
    ArkDPAVMPoliciesStats,
    ArkDPAVMPolicy,
    ArkDPAVMPolicyListItem,
    ArkDPAVMProvidersDict,
    ArkDPAVMUpdatePolicy,
    serialize_dpa_vm_policies_protocol_type,
    serialize_dpa_vm_policies_workspace_type,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-policies-vm', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
VM_POLICIES_API: Final[str] = 'api/access-policies'
VM_POLICY_API: Final[str] = 'api/access-policies/{policy_id}'
VM_UPDATE_POLICY_STATUS_API: Final[str] = 'api/access-policies/{policy_id}/status'


class ArkDPAVMPoliciesService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')

    @property
    def isp_client(self) -> ArkISPServiceClient:
        return self.__client

    def __policy_id_by_name(self, policy_name: str) -> str:
        policies = self.list_policies_by(ArkDPAVMPoliciesFilter(name=policy_name))
        if not policies:
            raise ArkServiceException(f'Failed to find vm policy id by name [{policy_name}]')
        return policies[0].policy_id

    @staticmethod
    def __serialize_providers_dict(providers_data: ArkDPAVMProvidersDict) -> Dict:
        serialized_providers_data = {}
        for k in list(providers_data.keys()):
            serialized_providers_data[serialize_dpa_vm_policies_workspace_type(k)] = providers_data[k].dict(by_alias=True)
        return serialized_providers_data

    @staticmethod
    def __serialize_authorization_rules_dict(authorization_rules: List[Dict]) -> None:
        for rule in authorization_rules:
            for k in list(rule['connectionInformation']['connectAs'].keys()):
                for pk in list(rule['connectionInformation']['connectAs'][k].keys()):
                    item = rule['connectionInformation']['connectAs'][k][pk]
                    del rule['connectionInformation']['connectAs'][k][pk]
                    rule['connectionInformation']['connectAs'][k][serialize_dpa_vm_policies_protocol_type(pk)] = item
                item = rule['connectionInformation']['connectAs'][k]
                del rule['connectionInformation']['connectAs'][k]
                rule['connectionInformation']['connectAs'][serialize_dpa_vm_policies_workspace_type(k)] = item

    def add_policy(self, add_policy: ArkDPAVMAddPolicy) -> ArkDPAVMPolicy:
        """
        Adds a new VM policy with the specified information.

        Args:
            add_policy (ArkDPVMAAddPolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPAVMPolicy: _description_
        """
        self._logger.info(f'Adding new vm policy [{add_policy.policy_name}]')
        add_policy_dict = add_policy.dict(by_alias=True)
        add_policy_dict['providersData'] = self.__serialize_providers_dict(add_policy.providers_data)
        self.__serialize_authorization_rules_dict(add_policy_dict['userAccessRules'])
        resp: Response = self.__client.post(VM_POLICIES_API, json=add_policy_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                policy_id = resp.json()['policyId']
                return self.policy(ArkDPAGetPolicy(policy_id=policy_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add vm policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add vm policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add vm policy [{resp.text}] - [{resp.status_code}]')

    def delete_policy(self, delete_policy: ArkDPADeletePolicy) -> None:
        """
        Deletes the specified (ID or name) VM policy.

        Args:
            delete_policy (ArkDPADeletePolicy): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_policy.policy_name and not delete_policy.policy_id:
            delete_policy.policy_id = self.__policy_id_by_name(delete_policy.policy_name)
        self._logger.info(f'Deleting vm policy [{delete_policy.policy_id}]')
        resp: Response = self.__client.delete(VM_POLICY_API.format(policy_id=delete_policy.policy_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete vm policy [{resp.text}] - [{resp.status_code}]')

    def update_policy(self, update_policy: ArkDPAVMUpdatePolicy) -> ArkDPAVMPolicy:
        """
        Updates a VM policy.

        Args:
            update_policy (ArkDPAVMUpdatePolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPAVMPolicy: _description_
        """
        if update_policy.policy_name and not update_policy.policy_id:
            update_policy.policy_id = self.__policy_id_by_name(update_policy.policy_name)
        self._logger.info(f'Updating vm policy [{update_policy.policy_id}]')
        update_dict = json.loads(update_policy.json(by_alias=True, exclude_none=True, exclude={'new_policy_name', 'policy_name'}))
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
                return ArkDPAVMPolicy.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update vm policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update vm policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update vm policy [{resp.text}] - [{resp.status_code}]')

    def update_policy_status(self, update_policy_status: ArkDPAUpdatePolicyStatus) -> ArkDPAVMPolicy:
        """
        Updates the status of the specified (by ID) VM policy.

        Args:
            update_policy_status (ArkDPAUpdatePolicyStatus): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPAVMPolicy: _description_
        """
        if update_policy_status.policy_name and not update_policy_status.policy_id:
            update_policy_status.policy_id = self.__policy_id_by_name(update_policy_status.policy_name)
        self._logger.info(f'Updating vm policy status [{update_policy_status.policy_id}]')
        resp: Response = self.__client.put(
            VM_UPDATE_POLICY_STATUS_API.format(policy_id=update_policy_status.policy_id),
            json=update_policy_status.dict(exclude={'policy_id'}),
        )
        if resp.status_code == HTTPStatus.OK:
            return self.policy(ArkDPAGetPolicy(policy_id=update_policy_status.policy_id))
        raise ArkServiceException(f'Failed to update vm policy status [{resp.text}] - [{resp.status_code}]')

    def list_policies(self) -> List[ArkDPAVMPolicyListItem]:
        """
        Lists all of the tenants's VM policies.

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkDPAVMPolicyListItem]: _description_
        """
        self._logger.info('Retrieving all vm policies')
        resp: Response = self.__client.get(VM_POLICIES_API)
        if resp.status_code == HTTPStatus.OK:
            try:
                return parse_obj_as(List[ArkDPAVMPolicyListItem], resp.json()['items'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list vm policies response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list vm policies response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list vm policies [{resp.text}] - [{resp.status_code}]')

    def list_policies_by(self, policies_filter: ArkDPAVMPoliciesFilter) -> List[ArkDPAVMPolicyListItem]:
        """
        Lists VM policies that match the specified filters.

        Args:
            policies_filter (ArkDPAVMPoliciesFilter): _description_

        Returns:
            List[ArkDPAVMPolicyListItem]: _description_
        """
        self._logger.info(f'Retrieving vm policies by filter [{policies_filter}]')
        policies = self.list_policies()

        # Filter by statuses
        if policies_filter.statuses:
            policies = [p for p in policies if p.status in policies_filter.statuses]

        # Filter by name wildcard
        if policies_filter.name:
            policies = [p for p in policies if fnmatch(p.policy_name, policies_filter.name)]

        # Filter by cloud providers
        if policies_filter.providers:
            policies = [p for p in policies if all(cp.value in p.platforms for cp in policies_filter.providers)]

        return policies

    def policy(self, get_policy: ArkDPAGetPolicy) -> ArkDPAVMPolicy:
        """
        Retrieves a VM policy by ID.

        Args:
            get_policy (ArkDPAGetPolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPAVMPolicy: _description_
        """
        if get_policy.policy_name and not get_policy.policy_id:
            get_policy.policy_id = self.__policy_id_by_name(get_policy.policy_name)
        self._logger.info(f'Retrieving vm policy [{get_policy.policy_id}]')
        resp: Response = self.__client.get(VM_POLICY_API.format(policy_id=get_policy.policy_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPAVMPolicy.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse vm policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse vm policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve vm policy [{get_policy.policy_id}] [{resp.text}] - [{resp.status_code}]')

    def policies_stats(self) -> ArkDPAVMPoliciesStats:
        """
        Calculates VM policy statistics.

        Returns:
            ArkDPAVMPoliciesStats: _description_
        """
        self._logger.info('Calculating vm policies stats')
        policies = self.list_policies()
        policies_stats = ArkDPAVMPoliciesStats.construct()
        policies_stats.policies_count = len(policies)

        # Count policies per status
        status_types: Set[ArkDPARuleStatus] = {p.status for p in policies if p.status}
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
