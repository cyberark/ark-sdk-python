from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List, Optional, Set

from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.secrets.db import (
    SECRET_TYPE_TO_STORE_DICT,
    ArkDPADBAddSecret,
    ArkDPADBDeleteSecret,
    ArkDPADBDisableSecret,
    ArkDPADBEnableSecret,
    ArkDPADBGetSecret,
    ArkDPADBSecretMetadata,
    ArkDPADBSecretMetadataList,
    ArkDPADBSecretsFilter,
    ArkDPADBSecretsStats,
    ArkDPADBSecretType,
    ArkDPADBStoreType,
    ArkDPADBUpdateSecret,
)
from ark_sdk_python.models.services.dpa.workspaces.db import ArkDPADBTag
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-secrets-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
SECRETS_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets'
SECRET_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets/{secret_id}'
ENABLE_SECRET_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets/{secret_id}/enable'
DISABLE_SECRET_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets/{secret_id}/disable'


class ArkDPADBSecretsService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')

    def __list_secrets_with_filters(
        self,
        secret_type: Optional[ArkDPADBSecretType] = None,
        tags: Optional[List[ArkDPADBTag]] = None,
    ) -> ArkDPADBSecretMetadataList:
        params = {}
        if secret_type:
            params['secret_type'] = secret_type.value
        if tags:
            params.update({t.key: t.value for t in tags})
        resp: Response = self.__client.get(SECRETS_ROUTE, params=params)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPADBSecretMetadataList.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse list secrets response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list secrets response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list secrets [{resp.text}] - [{resp.status_code}]')

    def add_secret(self, add_secret: ArkDPADBAddSecret) -> ArkDPADBSecretMetadata:
        """
        Adds a new DB secret to the secret store.

        Args:
            add_secret (ArkDPADBAddSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBSecretMetadata: _description_
        """
        self._logger.info('Adding new db secret')
        add_secret_dict = add_secret.dict(exclude_none=True, exclude={'store_type', 'username', 'password', 'pam_safe', 'pam_account_name'})
        if not add_secret.store_type:
            add_secret.store_type = SECRET_TYPE_TO_STORE_DICT[add_secret.secret_type]
        add_secret_dict['secret_store'] = {
            'store_type': add_secret.store_type.value,
        }
        if add_secret.secret_type == ArkDPADBSecretType.UsernamePassword:
            if not add_secret.username or not add_secret.password:
                raise ArkServiceException(
                    'When specifying a username password type, both username and password parameters must be supplied'
                )
            add_secret_dict['secret_data'] = {
                'username': add_secret.username,
                'password': add_secret.password.get_secret_value(),
            }
        elif add_secret.secret_type == ArkDPADBSecretType.CyberArkPAM:
            if not add_secret.pam_account_name or not add_secret.pam_safe:
                raise ArkServiceException(
                    'When specifying a pam secret type, both pam safe and pam account name parameters must be supplied'
                )
            add_secret_dict['secret_link'] = {
                'safe': add_secret.pam_safe,
                'account_name': add_secret.pam_account_name,
            }
        resp: Response = self.__client.post(
            SECRETS_ROUTE,
            json=add_secret_dict,
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkDPADBSecretMetadata.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add db secret [{resp.text}] - [{resp.status_code}]')

    def update_secret(self, update_secret: ArkDPADBUpdateSecret) -> ArkDPADBSecretMetadata:
        """
        Updates a DB secret.

        Args:
            update_secret (ArkDPADBUpdateSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBSecretMetadata: _description_
        """
        if update_secret.secret_name and not update_secret.secret_id:
            update_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkDPADBSecretsFilter(secret_name=update_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Updating existing db secret with id [{update_secret.secret_id}]')
        update_secret_dict = update_secret.dict(
            exclude_none=True,
            exclude={'secret_id', 'secret_name', 'new_secret_name', 'username', 'password', 'pam_safe', 'pam_account_name'},
        )
        if update_secret.new_secret_name:
            update_secret_dict['secret_name'] = update_secret.new_secret_name
        if update_secret.pam_account_name or update_secret.pam_safe:
            if not update_secret.pam_account_name or not update_secret.pam_safe:
                raise ArkServiceException('When specifying a pam secret, both pam safe and pam account name parameters must be supplied')
            update_secret_dict['secret_link'] = {
                'safe': update_secret.pam_safe,
                'account_name': update_secret.pam_account_name,
            }
        if update_secret.username or update_secret.password:
            if not update_secret.username or not update_secret.password:
                raise ArkServiceException(
                    'When specifying a username password secret, both username and password name parameters must be supplied'
                )
            update_secret_dict['secret_data'] = {
                'username': update_secret.username,
                'password': update_secret.password.get_secret_value(),
            }
        resp: Response = self.__client.post(
            SECRET_ROUTE.format(secret_id=update_secret.secret_id),
            json=update_secret_dict,
        )
        if resp.status_code == HTTPStatus.OK:
            return self.secret(ArkDPADBSecretMetadata(secret_id=update_secret.secret_id))
        raise ArkServiceException(f'Failed to update db secret [{resp.text}] - [{resp.status_code}]')

    def delete_secret(self, delete_secret: ArkDPADBDeleteSecret) -> None:
        """
        Deletes a DB secret.

        Args:
            delete_secret (ArkDPADBDeleteSecret): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_secret.secret_name and not delete_secret.secret_id:
            delete_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkDPADBSecretsFilter(secret_name=delete_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Deleting db secret by id [{delete_secret.secret_id}]')
        resp: Response = self.__client.delete(SECRET_ROUTE.format(secret_id=delete_secret.secret_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete db secret [{resp.text}] - [{resp.status_code}]')

    def list_secrets(self) -> ArkDPADBSecretMetadataList:
        """
        Lists all tenant DB secrets.

        Returns:
            ArkDPADBSecretMetadataList: _description_
        """
        self._logger.info('Listing all db secrets')
        return self.__list_secrets_with_filters()

    def list_secrets_by(self, secrets_filter: ArkDPADBSecretsFilter) -> ArkDPADBSecretMetadataList:
        """
        Lists DB secrets that match the specified filters.

        Args:
            secrets_filter (ArkDPADBSecretsFilter): _description_

        Returns:
            ArkDPADBSecretMetadataList: _description_
        """
        self._logger.info(f'Listing db secrets by filters [{secrets_filter}]')
        secrets = self.__list_secrets_with_filters(secrets_filter.secret_type, secrets_filter.tags)

        # Filter by secret types
        if secrets_filter.store_type:
            secrets.secrets = [s for s in secrets.secrets if s.secret_store.store_type == secrets_filter.store_type]

        # Filter by name
        if secrets_filter.secret_name:
            secrets.secrets = [s for s in secrets.secrets if s.secret_name and fnmatch(s.secret_name, secrets_filter.secret_name)]

        # Filter by is active
        if secrets_filter.is_active is not None:
            secrets.secrets = [s for s in secrets.secrets if s.is_active == secrets_filter.is_active]
        secrets.total_count = len(secrets.secrets)

        return secrets

    def enable_secret(self, enable_secret: ArkDPADBEnableSecret) -> ArkDPADBSecretMetadata:
        """
        Enables a DB secret.

        Args:
            enable_secret (ArkDPADBEnableSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBSecretMetadata: _description_
        """
        if enable_secret.secret_name and not enable_secret.secret_id:
            enable_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkDPADBSecretsFilter(secret_name=enable_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Enabling db secret by id [{enable_secret.secret_id}]')
        resp: Response = self.__client.post(ENABLE_SECRET_ROUTE.format(secret_id=enable_secret.secret_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPADBSecretMetadata.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse enable db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse enable db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve enable db secret [{resp.text}] - [{resp.status_code}]')

    def disable_secret(self, disable_secret: ArkDPADBDisableSecret) -> ArkDPADBSecretMetadata:
        """
        Disables a DB secret.

        Args:
            disable_secret (ArkDPADBDisableSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBSecretMetadata: _description_
        """
        if disable_secret.secret_name and not disable_secret.secret_id:
            disable_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkDPADBSecretsFilter(secret_name=disable_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Disabling db secret by id [{disable_secret.secret_id}]')
        resp: Response = self.__client.post(DISABLE_SECRET_ROUTE.format(secret_id=disable_secret.secret_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPADBSecretMetadata.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse disable db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse disable db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve disable db secret [{resp.text}] - [{resp.status_code}]')

    def secret(self, get_secret: ArkDPADBGetSecret) -> ArkDPADBSecretMetadata:
        """
        Retrieves a DB secret.

        Args:
            get_secret (ArkDPADBGetSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkDPADBSecretMetadata: _description_
        """
        if get_secret.secret_name and not get_secret.secret_id:
            get_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkDPADBSecretsFilter(secret_name=get_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Retrieving db secret by id [{get_secret.secret_id}]')
        resp: Response = self.__client.get(SECRET_ROUTE.format(secret_id=get_secret.secret_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkDPADBSecretMetadata.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve db secret [{resp.text}] - [{resp.status_code}]')

    def secrets_stats(self) -> ArkDPADBSecretsStats:
        """
        Calculates DB secrets statistics.

        Returns:
            ArkDPADBSecretsStats: _description_
        """
        self._logger.info('Calculating secrets statistics')
        secrets = self.list_secrets()
        secrets_stats = ArkDPADBSecretsStats.construct()
        secrets_stats.secrets_count = len(secrets.secrets)
        secrets_stats.active_secrets_count = len([s for s in secrets.secrets if s.is_active])
        secrets_stats.inactive_secrets_count = len([s for s in secrets.secrets if not s.is_active])

        # Count secrets per secret type
        secret_types: Set[ArkDPADBSecretType] = {s.secret_type for s in secrets.secrets if s.secret_type}
        secrets_stats.secrets_count_by_secret_type = {
            st: len([s for s in secrets.secrets if s.secret_type and s.secret_type == st]) for st in secret_types
        }

        # Count secrets per store type
        store_types: Set[ArkDPADBStoreType] = {s.secret_store.store_type for s in secrets.secrets if s.secret_store.store_type}
        secrets_stats.secrets_count_by_store_type = {
            st: len([s for s in secrets.secrets if s.secret_store.store_type and s.secret_store.store_type == st]) for st in store_types
        }

        return secrets_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
