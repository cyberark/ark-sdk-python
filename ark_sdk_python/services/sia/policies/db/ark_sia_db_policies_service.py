import json
from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List, Set

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.policies.common import (
    ArkSIADeletePolicy,
    ArkSIAGetPolicy,
    ArkSIARuleStatus,
    ArkSIAUpdatePolicyStatus,
)
from ark_sdk_python.models.services.sia.policies.db import (
    ArkSIADBAddPolicy,
    ArkSIADBPoliciesFilter,
    ArkSIADBPoliciesStats,
    ArkSIADBPolicy,
    ArkSIADBPolicyListItem,
    ArkSIADBUpdatePolicy,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-policies-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
DB_POLICIES_API: Final[str] = 'api/adb/access-policies'
DB_POLICY_API: Final[str] = 'api/adb/access-policies/{policy_id}'
DB_UPDATE_POLICY_STATUS_API: Final[str] = 'api/adb/access-policies/{policy_id}/status'


class ArkSIADBPoliciesService(ArkService):
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
        policies = self.list_policies_by(ArkSIADBPoliciesFilter(name=policy_name))
        if not policies:
            raise ArkServiceException(f'Failed to find db policy id by name [{policy_name}]')
        return policies[0].policy_id

    def add_policy(self, add_policy: ArkSIADBAddPolicy) -> ArkSIADBPolicy:
        """
        Adds a new DB policy with the specified information.

        Args:
            add_policy (ArkSIADBAddPolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBPolicy: _description_
        """
        self._logger.info(f'Adding new db policy [{add_policy.policy_name}]')
        add_policy_dict = add_policy.model_dump(by_alias=True, exclude_none=True)
        resp: Response = self.__client.post(DB_POLICIES_API, json=add_policy_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                policy_id = resp.json()['policyId']
                return self.policy(ArkSIAGetPolicy(policy_id=policy_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add db policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add sb policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add db policy [{resp.text}] - [{resp.status_code}]')

    def delete_policy(self, delete_policy: ArkSIADeletePolicy) -> None:
        """
        Deletes the specified (ID or name) DB policy.

        Args:
            delete_policy (ArkSIADeletePolicy): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_policy.policy_name and not delete_policy.policy_id:
            delete_policy.policy_id = self.__policy_id_by_name(delete_policy.policy_name)
        self._logger.info(f'Deleting db policy [{delete_policy.policy_id}]')
        resp: Response = self.__client.delete(DB_POLICY_API.format(policy_id=delete_policy.policy_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete db policy [{resp.text}] - [{resp.status_code}]')

    def update_policy(self, update_policy: ArkSIADBUpdatePolicy) -> ArkSIADBPolicy:
        """
        Updates a DB policy.

        Args:
            update_policy (ArkSIADBUpdatePolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBPolicy: _description_
        """
        if update_policy.policy_name and not update_policy.policy_id:
            update_policy.policy_id = self.__policy_id_by_name(update_policy.policy_name)
        self._logger.info(f'Updating db policy [{update_policy.policy_id}]')
        update_dict = json.loads(
            update_policy.model_dump_json(by_alias=True, exclude_none=True, exclude={'new_policy_name', 'policy_name'})
        )
        if update_policy.new_policy_name:
            update_dict['policyName'] = update_policy.new_policy_name
        else:
            update_dict['policyName'] = update_policy.policy_name
        resp: Response = self.__client.put(DB_POLICY_API.format(policy_id=update_policy.policy_id), json=update_dict)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBPolicy.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update db policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update db policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update db policy [{resp.text}] - [{resp.status_code}]')

    def update_policy_status(self, update_policy_status: ArkSIAUpdatePolicyStatus) -> ArkSIADBPolicy:
        """
        Updates the status of the specified (by ID) DB policy.

        Args:
            update_policy_status (ArkSIAUpdatePolicyStatus): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBPolicy: _description_
        """
        if update_policy_status.policy_name and not update_policy_status.policy_id:
            update_policy_status.policy_id = self.__policy_id_by_name(update_policy_status.policy_name)
        self._logger.info(f'Updating db policy status [{update_policy_status.policy_id}]')
        resp: Response = self.__client.put(
            DB_UPDATE_POLICY_STATUS_API.format(policy_id=update_policy_status.policy_id),
            json=update_policy_status.model_dump(exclude={'policy_id'}),
        )
        if resp.status_code == HTTPStatus.OK:
            return self.policy(ArkSIAGetPolicy(policy_id=update_policy_status.policy_id))
        raise ArkServiceException(f'Failed to update db policy status [{resp.text}] - [{resp.status_code}]')

    def list_policies(self) -> List[ArkSIADBPolicyListItem]:
        """
        Lists all of the tenants's DB policies.

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkSIADBPolicyListItem]: _description_
        """
        self._logger.info('Retrieving all db policies')
        resp: Response = self.__client.get(DB_POLICIES_API)
        if resp.status_code == HTTPStatus.OK:
            try:
                return TypeAdapter(List[ArkSIADBPolicyListItem]).validate_python(resp.json()['items'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list db policies response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list db policies response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list db policies [{resp.text}] - [{resp.status_code}]')

    def list_policies_by(self, policies_filter: ArkSIADBPoliciesFilter) -> List[ArkSIADBPolicyListItem]:
        """
        Lists DB policies that match the specified filters.

        Args:
            policies_filter (ArkSIADBPoliciesFilter): _description_

        Returns:
            List[ArkSIADBPolicyListItem]: _description_
        """
        self._logger.info(f'Retrieving db policies by filter [{policies_filter}]')
        policies = self.list_policies()

        # Filter by statuses
        if policies_filter.statuses:
            policies = [p for p in policies if p.status in policies_filter.statuses]

        # Filter by name wildcard
        if policies_filter.name:
            policies = [p for p in policies if fnmatch(p.policy_name, policies_filter.name)]

        # Filter by cloud providers
        if policies_filter.providers:
            policies = [p for p in policies if all(cp.value in p.providers for cp in policies_filter.providers)]

        return policies

    def policy(self, get_policy: ArkSIAGetPolicy) -> ArkSIADBPolicy:
        """
        Retrieves a DB policy by ID.

        Args:
            get_policy (ArkSIAGetPolicy): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBPolicy: _description_
        """
        if get_policy.policy_name and not get_policy.policy_id:
            get_policy.policy_id = self.__policy_id_by_name(get_policy.policy_name)
        self._logger.info(f'Retrieving db policy [{get_policy.policy_id}]')
        resp: Response = self.__client.get(DB_POLICY_API.format(policy_id=get_policy.policy_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBPolicy.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse db policy response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse db policy response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve db policy [{get_policy.policy_id}] [{resp.text}] - [{resp.status_code}]')

    def policies_stats(self) -> ArkSIADBPoliciesStats:
        """
        Calculates policy statistics.

        Returns:
            ArkSIADBPoliciesStats: _description_
        """
        self._logger.info('Calculating db policies stats')
        policies = self.list_policies()
        policies_stats = ArkSIADBPoliciesStats.model_construct()
        policies_stats.policies_count = len(policies)

        # Count policies per status
        status_types: Set[ArkSIARuleStatus] = {p.status for p in policies if p.status}
        policies_stats.policies_count_per_status = {st: len([p for p in policies if p.status and p.status == st]) for st in status_types}

        # Count policies per platforms
        policies_stats.policies_count_per_provider = {}
        for policy in policies:
            for platform in policy.providers:
                if platform not in policies_stats.policies_count_per_provider:
                    policies_stats.policies_count_per_provider[platform] = 0
                policies_stats.policies_count_per_provider[platform] += 1

        return policies_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
