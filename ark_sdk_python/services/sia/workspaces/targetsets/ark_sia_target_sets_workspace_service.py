from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List, Set

from overrides import overrides
from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.secrets.vm import ArkSIAVMSecretType
from ark_sdk_python.models.services.sia.workspaces.targetsets import (
    ArkSIAAddTargetSet,
    ArkSIADeleteTargetSet,
    ArkSIAGetTargetSet,
    ArkSIATargetSet,
    ArkSIATargetSetsFilter,
    ArkSIATargetSetsStats,
    ArkSIAUpdateTargetSet,
)
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_bulk_add_target_sets import ArkSIABulkAddTargetSetsItem
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_bulk_delete_target_sets import ArkSIABulkDeleteTargetSets
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_bulk_target_set_response import ArkSIABulkTargetSetResponse
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-workspaces-target-sets', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
TARGET_SETS_API: Final[str] = 'api/targetsets'
BULK_TARGET_SETS_API: Final[str] = 'api/targetsets/bulk'
TARGET_SET_API: Final[str] = 'api/targetsets/{target_name}'


class ArkSIATargetSetsWorkspaceService(ArkService):
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

    def add_target_set(self, add_target_set: ArkSIAAddTargetSet) -> ArkSIATargetSet:
        """
        Add a new target set

        Args:
            add_target_set (ArkSIAAddTargetSet): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIATargetSet: _description_
        """
        self._logger.info(f'Adding target set [{add_target_set.name}]')
        add_target_set_dict = add_target_set.model_dump()
        resp: Response = self.__client.post(TARGET_SETS_API, json=add_target_set_dict)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                add_target_set_dict.update(resp.json()['target_set'])
                return ArkSIATargetSet(**add_target_set_dict)
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse add target set response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add target set response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add target set [{resp.text}] - [{resp.status_code}]')

    def bulk_add_target_sets(self, bulk_add_target_sets: ArkSIABulkAddTargetSetsItem) -> ArkSIABulkTargetSetResponse:
        """
        Bulk add new target sets

        Args:
            bulk_add_target_sets (ArkSIABulkAddTargetSet): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIABulkTargetSetResponse: _description_
        """
        self._logger.info(f'Bulk adding target sets [{bulk_add_target_sets}]')
        resp: Response = self.__client.post(BULK_TARGET_SETS_API, json=bulk_add_target_sets.model_dump())
        if resp.status_code == HTTPStatus.MULTI_STATUS:
            try:
                return ArkSIABulkTargetSetResponse.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse bulk add target set response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse bulk add target set response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to bulk add target sets [{resp.text}] - [{resp.status_code}]')

    def delete_target_set(self, delete_target_set: ArkSIADeleteTargetSet) -> None:
        """
        Delete an existing target set

        Args:
            delete_target_set (ArkSIADeleteTargetSet): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting target set [{delete_target_set.name}]')
        resp: Response = self.__client.delete(TARGET_SET_API.format(target_name=delete_target_set.name))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete target set [{resp.text}] - [{resp.status_code}]')

    def bulk_delete_target_sets(self, bulk_delete_target_sets: ArkSIABulkDeleteTargetSets) -> ArkSIABulkTargetSetResponse:
        """
        Bulk deletes existing target sets

        Args:
            bulk_delete_target_sets (ArkSIABulkDeleteTargetSet): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIABulkTargetSetResponse: _description_
        """
        self._logger.info(f'Bulk deleting target sets [{bulk_delete_target_sets}]')
        resp: Response = self.__client.delete(BULK_TARGET_SETS_API, json=bulk_delete_target_sets.target_sets)
        if resp.status_code == HTTPStatus.MULTI_STATUS:
            try:
                return ArkSIABulkTargetSetResponse.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse bulk delete target set response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse bulk delete target set response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to bulk delete target sets [{resp.text}] - [{resp.status_code}]')

    def update_target_set(self, update_target_set: ArkSIAUpdateTargetSet) -> ArkSIATargetSet:
        """
        Update an existing target set

        Args:
            update_target_set (ArkSIAUpdateTargetSet): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIATargetSet: _description_
        """
        self._logger.info(f'Updating target set [{update_target_set.name}]')
        update_target_set_dict = update_target_set.model_dump(exclude={'name', 'new_name'}, exclude_none=True)
        if update_target_set.new_name:
            update_target_set_dict["name"] = update_target_set.new_name
        resp: Response = self.__client.put(TARGET_SET_API.format(target_name=update_target_set.name), json=update_target_set_dict)
        if resp.status_code == HTTPStatus.OK:
            try:
                update_target_set_dict.update(resp.json()['target_set'])
                return ArkSIATargetSet(**update_target_set_dict)
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse update target set response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update target set response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update target set [{resp.text}] - [{resp.status_code}]')

    def list_target_sets(self) -> List[ArkSIATargetSet]:
        """
        List all target sets

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkSIATargetSet]: _description_
        """
        self._logger.info('Listing all target sets')
        resp: Response = self.__client.get(TARGET_SETS_API)
        if resp.status_code == HTTPStatus.OK:
            try:
                return [ArkSIATargetSet.model_validate(ts) for ts in resp.json()['target_sets']]
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list target sets response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list target sets response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list target sets [{resp.text}] - [{resp.status_code}]')

    def list_target_sets_by(self, target_sets_filter: ArkSIATargetSetsFilter) -> List[ArkSIATargetSet]:
        """
        List target sets by given filters

        Args:
            target_sets_filter (ArkSIATargetSetsFilter): _description_

        Returns:
            List[ArkSIATargetSet]: _description_
        """
        self._logger.info(f'Listing target sets by filters [{target_sets_filter}]')
        target_sets = self.list_target_sets()
        if target_sets_filter.name:
            target_sets = [t for t in target_sets if fnmatch(t.name, target_sets_filter.name)]
        if target_sets_filter.secret_type:
            target_sets = [t for t in target_sets if t.secret_type and t.secret_type == target_sets_filter.secret_type]
        return target_sets

    def target_set(self, get_target_set: ArkSIAGetTargetSet) -> ArkSIATargetSet:
        """
        Get specific target set

        Args:
            get_target_set (ArkSIAGetTargetSet): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIATargetSet: _description_
        """
        self._logger.info(f'Getting target set [{get_target_set.name}]')
        resp: Response = self.__client.get(TARGET_SET_API.format(target_name=get_target_set.name))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIATargetSet(**resp.json()['target_set'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse target set response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse target set response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to get target set [{resp.text}] - [{resp.status_code}]')

    def target_sets_stats(self) -> ArkSIATargetSetsStats:
        """
        Calculate stats about the target sets of the tenant

        Returns:
            ArkSIATargetSetsStats: _description_
        """
        self._logger.info('Calculating target sets stats')
        target_sets = self.list_target_sets()
        target_sets_stats = ArkSIATargetSetsStats.model_construct()
        target_sets_stats.target_sets_count = len(target_sets)

        # Get target_sets per secret type
        secret_types: Set[ArkSIAVMSecretType] = {d.secret_type for d in target_sets if d.secret_type}
        target_sets_stats.target_sets_count_per_secret_type = {
            st: len([d for d in target_sets if d.secret_type and d.secret_type == st]) for st in secret_types
        }

        return target_sets_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
