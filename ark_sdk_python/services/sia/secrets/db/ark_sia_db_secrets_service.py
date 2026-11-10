import re
from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, Iterator, List, Optional, Set

from overrides import overrides
from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkPage
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.secrets.db import (
    SECRET_TYPE_TO_STORE_DICT,
    ArkSIADBAddSecret,
    ArkSIADBAddStrongAccount,
    ArkSIADBAddStrongAccountResponse,
    ArkSIADBDeleteSecret,
    ArkSIADBDeleteStrongAccount,
    ArkSIADBDisableSecret,
    ArkSIADBEnableSecret,
    ArkSIADBGetSecret,
    ArkSIADBGetStrongAccount,
    ArkSIADBSecretMetadata,
    ArkSIADBSecretMetadataList,
    ArkSIADBSecretsFilter,
    ArkSIADBSecretsStats,
    ArkSIADBSecretType,
    ArkSIADBStoreType,
    ArkSIADBStrongAccountMetadata,
    ArkSIADBStrongAccountsFilter,
    ArkSIADBUpdateSecret,
    ArkSIADBUpdateStrongAccount,
)
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_list_strong_accounts_response import ArkSIADBListStrongAccountsResponse
from ark_sdk_python.models.services.sia.workspaces.db import ArkSIADBTag
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-secrets-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
SECRETS_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets'
SECRET_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets/{secret_id}'
ENABLE_SECRET_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets/{secret_id}/enable'
DISABLE_SECRET_ROUTE: Final[str] = 'api/adb/secretsmgmt/secrets/{secret_id}/disable'
STRONG_ACCOUNTS_ROUTE: Final[str] = '/api/database-strong-accounts'
STRONG_ACCOUNT_ROUTE: Final[str] = '/api/database-strong-accounts/{strong_account_id}'

ArkSIADBStrongAccountsPage = ArkPage[ArkSIADBStrongAccountMetadata]


class ArkSIADBSecretsService(ArkService):
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

    def __list_secrets_with_filters(
        self,
        secret_type: Optional[ArkSIADBSecretType] = None,
        tags: Optional[List[ArkSIADBTag]] = None,
    ) -> ArkSIADBSecretMetadataList:
        params = {}
        if secret_type:
            params['secret_type'] = secret_type.value
        if tags:
            params.update({t.key: t.value for t in tags})
        resp: Response = self.__client.get(SECRETS_ROUTE, params=params)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBSecretMetadataList.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse list secrets response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list secrets response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list secrets [{resp.text}] - [{resp.status_code}]')

    def add_secret(self, add_secret: ArkSIADBAddSecret) -> ArkSIADBSecretMetadata:
        """
        Adds a new DB secret to the secret store.

        Args:
            add_secret (ArkSIADBAddSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBSecretMetadata: _description_
        """
        self._logger.warning(
            "Deprecated: Use add_strong_account instead. This method uses the legacy API which will be removed in a future version."
        )

        self._logger.info('Adding new db secret')
        add_secret_dict = add_secret.model_dump(
            exclude_none=True,
            exclude={
                'store_type',
                'username',
                'password',
                'pam_safe',
                'pam_account_name',
                'iam_username',
                'iam_account',
                'iam_access_key_id',
                'iam_secret_access_key',
                'atlas_public_key',
                'atlas_private_key',
            },
        )
        if not add_secret.store_type:
            add_secret.store_type = SECRET_TYPE_TO_STORE_DICT[add_secret.secret_type]
        add_secret_dict['secret_store'] = {
            'store_type': add_secret.store_type.value,
        }
        if add_secret.secret_type == ArkSIADBSecretType.UsernamePassword:
            if not add_secret.username or not add_secret.password:
                raise ArkServiceException(
                    'When specifying a username password type, both username and password parameters must be supplied'
                )
            add_secret_dict['secret_data'] = {
                'username': add_secret.username,
                'password': add_secret.password.get_secret_value(),
            }
        elif add_secret.secret_type == ArkSIADBSecretType.CyberArkPAM:
            if not add_secret.pam_account_name or not add_secret.pam_safe:
                raise ArkServiceException(
                    'When specifying a pam secret type, both pam safe and pam account name parameters must be supplied'
                )
            add_secret_dict['secret_link'] = {
                'safe': add_secret.pam_safe,
                'account_name': add_secret.pam_account_name,
            }
        elif add_secret.secret_type == ArkSIADBSecretType.IAMUser:
            if (
                not add_secret.iam_access_key_id
                or not add_secret.iam_secret_access_key
                or not add_secret.iam_account
                or not add_secret.iam_username
            ):
                raise ArkServiceException('When specifying a iam user secret type, all iam parameters must be supplied')
            add_secret_dict['secret_data'] = {
                'account': add_secret.iam_account,
                'username': add_secret.iam_username,
                'access_key_id': add_secret.iam_access_key_id.get_secret_value(),
                'secret_access_key': add_secret.iam_secret_access_key.get_secret_value(),
            }
        elif add_secret.secret_type == ArkSIADBSecretType.AtlasAccessKeys:
            if not add_secret.atlas_public_key or not add_secret.atlas_private_key:
                raise ArkServiceException(
                    'When specifying an atlas secret type, both private key and public key parameters must be supplied'
                )
            add_secret_dict['secret_data'] = {
                'public_key': add_secret.atlas_public_key,
                'private_key': add_secret.atlas_private_key.get_secret_value(),
            }
        resp: Response = self.__client.post(
            SECRETS_ROUTE,
            json=add_secret_dict,
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkSIADBSecretMetadata.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add db secret [{resp.text}] - [{resp.status_code}]')

    def update_secret(self, update_secret: ArkSIADBUpdateSecret) -> ArkSIADBSecretMetadata:
        """
        Updates a DB secret.

        Args:
            update_secret (ArkSIADBUpdateSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBSecretMetadata: _description_
        """
        if update_secret.secret_name and not update_secret.secret_id:
            update_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkSIADBSecretsFilter(secret_name=update_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Updating existing db secret with id [{update_secret.secret_id}]')
        update_secret_dict = update_secret.model_dump(
            exclude_none=True,
            exclude={
                'secret_id',
                'secret_name',
                'new_secret_name',
                'username',
                'password',
                'pam_safe',
                'pam_account_name',
                'iam_username',
                'iam_account',
                'iam_access_key_id',
                'iam_secret_access_key',
                'atlas_public_key',
                'atlas_private_key',
            },
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
        if (
            update_secret.iam_access_key_id
            or update_secret.iam_secret_access_key
            or update_secret.iam_account
            or update_secret.iam_username
        ):
            if (
                not update_secret.iam_access_key_id
                or not update_secret.iam_secret_access_key
                or not update_secret.iam_account
                or not update_secret.iam_username
            ):
                raise ArkServiceException('When specifying a iam user secret type, all iam parameters must be supplied')
            update_secret_dict['secret_data'] = {
                'account': update_secret.iam_account,
                'username': update_secret.iam_username,
                'access_key_id': update_secret.iam_access_key_id.get_secret_value(),
                'secret_access_key': update_secret.iam_secret_access_key.get_secret_value(),
            }
        if update_secret.atlas_public_key or update_secret.atlas_private_key:
            if not update_secret.atlas_public_key or not update_secret.atlas_private_key:
                raise ArkServiceException('When specifying an atlas secret, both private key and public key parameters must be supplied')
            update_secret_dict['secret_data'] = {
                'public_key': update_secret.atlas_public_key,
                'private_key': update_secret.atlas_private_key.get_secret_value(),
            }

        resp: Response = self.__client.patch(
            SECRET_ROUTE.format(secret_id=update_secret.secret_id),
            json=update_secret_dict,
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBSecretMetadata.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update db secret [{resp.text}] - [{resp.status_code}]')

    def delete_secret(self, delete_secret: ArkSIADBDeleteSecret) -> None:
        """
        Deletes a DB secret.

        Args:
            delete_secret (ArkSIADBDeleteSecret): _description_

        Raises:
            ArkServiceException: _description_
        """
        if delete_secret.secret_name and not delete_secret.secret_id:
            delete_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkSIADBSecretsFilter(secret_name=delete_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Deleting db secret by id [{delete_secret.secret_id}]')
        resp: Response = self.__client.delete(SECRET_ROUTE.format(secret_id=delete_secret.secret_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete db secret [{resp.text}] - [{resp.status_code}]')

    def list_secrets(self) -> ArkSIADBSecretMetadataList:
        """
        Lists all tenant DB secrets.

        Returns:
            ArkSIADBSecretMetadataList: _description_
        """
        self._logger.info('Listing all db secrets')
        return self.__list_secrets_with_filters()

    def list_secrets_by(self, secrets_filter: ArkSIADBSecretsFilter) -> ArkSIADBSecretMetadataList:
        """
        Lists DB secrets that match the specified filters.

        Args:
            secrets_filter (ArkSIADBSecretsFilter): _description_

        Returns:
            ArkSIADBSecretMetadataList: _description_
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

    def enable_secret(self, enable_secret: ArkSIADBEnableSecret) -> ArkSIADBSecretMetadata:
        """
        Enables a DB secret.

        Args:
            enable_secret (ArkSIADBEnableSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBSecretMetadata: _description_
        """
        if enable_secret.secret_name and not enable_secret.secret_id:
            enable_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkSIADBSecretsFilter(secret_name=enable_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Enabling db secret by id [{enable_secret.secret_id}]')
        resp: Response = self.__client.post(ENABLE_SECRET_ROUTE.format(secret_id=enable_secret.secret_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to enable db secret [{resp.text}] - [{resp.status_code}]')

    def disable_secret(self, disable_secret: ArkSIADBDisableSecret) -> ArkSIADBSecretMetadata:
        """
        Disables a DB secret.

        Args:
            disable_secret (ArkSIADBDisableSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBSecretMetadata: _description_
        """
        if disable_secret.secret_name and not disable_secret.secret_id:
            disable_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkSIADBSecretsFilter(secret_name=disable_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Disabling db secret by id [{disable_secret.secret_id}]')
        resp: Response = self.__client.post(DISABLE_SECRET_ROUTE.format(secret_id=disable_secret.secret_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to disable db secret [{resp.text}] - [{resp.status_code}]')

    def secret(self, get_secret: ArkSIADBGetSecret) -> ArkSIADBSecretMetadata:
        """
        Retrieves a DB secret.

        Args:
            get_secret (ArkSIADBGetSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIADBSecretMetadata: _description_
        """
        if get_secret.secret_name and not get_secret.secret_id:
            get_secret.secret_id = (
                self.list_secrets_by(
                    secrets_filter=ArkSIADBSecretsFilter(secret_name=get_secret.secret_name),
                )
                .secrets[0]
                .secret_id
            )
        self._logger.info(f'Retrieving db secret by id [{get_secret.secret_id}]')
        resp: Response = self.__client.get(SECRET_ROUTE.format(secret_id=get_secret.secret_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBSecretMetadata.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse db secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse db secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve db secret [{resp.text}] - [{resp.status_code}]')

    def secrets_stats(self) -> ArkSIADBSecretsStats:
        """
        Calculates DB secrets statistics.

        Returns:
            ArkSIADBSecretsStats: _description_
        """
        self._logger.info('Calculating secrets statistics')
        secrets = self.list_secrets()
        secrets_stats = ArkSIADBSecretsStats.model_construct()
        secrets_stats.secrets_count = len(secrets.secrets)
        secrets_stats.active_secrets_count = len([s for s in secrets.secrets if s.is_active])
        secrets_stats.inactive_secrets_count = len([s for s in secrets.secrets if not s.is_active])

        # Count secrets per secret type
        secret_types: Set[ArkSIADBSecretType] = {s.secret_type for s in secrets.secrets if s.secret_type}
        secrets_stats.secrets_count_by_secret_type = {
            st: len([s for s in secrets.secrets if s.secret_type and s.secret_type == st]) for st in secret_types
        }

        # Count secrets per store type
        store_types: Set[ArkSIADBStoreType] = {s.secret_store.store_type for s in secrets.secrets if s.secret_store.store_type}
        secrets_stats.secrets_count_by_store_type = {
            st: len([s for s in secrets.secrets if s.secret_store.store_type and s.secret_store.store_type == st]) for st in store_types
        }

        return secrets_stats

    def add_strong_account(self, add_strong_account: ArkSIADBAddStrongAccount) -> ArkSIADBAddStrongAccountResponse:
        """
        Adds a new DB strong account to the secret store.

        Args:
            add_strong_account (ArkSIADBAddStrongAccount): The strong account details to add

        Raises:
            ArkServiceException: If validation fails or API request fails

        Returns:
            ArkSIADBAddStrongAccountResponse: Response with account ID and creation timestamp
        """
        self._logger.info('Adding new db strong account')

        request_payload = self._build_account_request(add_strong_account)
        self._logger.debug(f'Request payload: {request_payload}')

        resp: Response = self.__client.post(
            STRONG_ACCOUNTS_ROUTE,
            json=request_payload,
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkSIADBAddStrongAccountResponse.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add strong account response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add strong account response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add strong account [{resp.text}] - [{resp.status_code}]')

    def _build_account_request(self, add_strong_account: ArkSIADBAddStrongAccount) -> dict:
        store_type = add_strong_account.store_type.lower()

        if store_type == 'pam':
            return self._build_pam_account_request(add_strong_account)
        elif store_type == 'managed':
            return self._build_managed_account_request(add_strong_account)
        else:
            raise ArkServiceException(f'Invalid store_type: {store_type}. Must be "pam" or "managed"')

    def _build_pam_account_request(self, add_strong_account: ArkSIADBAddStrongAccount) -> dict:
        if not add_strong_account.safe:
            raise ArkServiceException('PAM account requires "safe" field')
        if not add_strong_account.account_name:
            raise ArkServiceException('PAM account requires "account_name" field')

        return {
            'store_type': 'pam',
            'name': add_strong_account.name,
            'account_properties': {
                'safe': add_strong_account.safe,
                'account_name': add_strong_account.account_name,
            },
        }

    def _build_managed_account_request(self, add_strong_account: ArkSIADBAddStrongAccount) -> dict:
        if not add_strong_account.platform:
            raise ArkServiceException('Managed account requires "platform" field')

        platform = add_strong_account.platform
        account_properties = self._build_account_properties(add_strong_account, platform)
        password_secret_object = self._build_password_secret_object(add_strong_account, platform)

        return {
            'store_type': 'managed',
            'name': add_strong_account.name,
            'account_properties': account_properties,
            'password_secret_object': password_secret_object,
        }

    def _build_account_properties(self, add_strong_account: ArkSIADBAddStrongAccount, platform: str) -> dict:
        if not add_strong_account.username:
            raise ArkServiceException(f'{platform} account requires "username" field')

        properties = {
            'platform': platform,
            'username': add_strong_account.username,
        }

        if platform == 'MongoDB':
            if not add_strong_account.address:
                raise ArkServiceException('MongoDB account requires "address" field')
            if not add_strong_account.database:
                raise ArkServiceException('MongoDB account requires "database" field')
            properties['address'] = add_strong_account.address
            properties['database'] = add_strong_account.database
            if add_strong_account.port:
                properties['port'] = add_strong_account.port
            if add_strong_account.auth_database:
                properties['authDatabase'] = add_strong_account.auth_database
            if add_strong_account.replica_set:
                properties['replicaSet'] = add_strong_account.replica_set
            if add_strong_account.use_ssl:
                properties['useSsl'] = add_strong_account.use_ssl
            if add_strong_account.dsn:
                properties['dsn'] = add_strong_account.dsn

        elif platform == 'DB2UnixSSH':
            if not add_strong_account.address:
                raise ArkServiceException('DB2UnixSSH account requires "address" field')
            properties['address'] = add_strong_account.address

        elif platform == 'WinDomain':
            if not add_strong_account.address:
                raise ArkServiceException('WinDomain account requires "address" field')
            properties['address'] = add_strong_account.address
            if add_strong_account.log_on_to:
                properties['logOnTo'] = add_strong_account.log_on_to
            if add_strong_account.user_dn:
                properties['userDN'] = add_strong_account.user_dn
            if add_strong_account.port:
                properties['port'] = add_strong_account.port

        elif platform == 'AWSAccessKeys':
            if not add_strong_account.aws_account_id:
                raise ArkServiceException('AWSAccessKeys account requires "aws_account_id" field')
            if not add_strong_account.aws_access_key_id:
                raise ArkServiceException('AWSAccessKeys account requires "aws_access_key_id" field')
            properties['awsAccountId'] = add_strong_account.aws_account_id
            properties['awsAccessKeyId'] = add_strong_account.aws_access_key_id
            if add_strong_account.aws_account_alias_name:
                properties['awsAccountAliasName'] = add_strong_account.aws_account_alias_name
            if add_strong_account.region:
                properties['region'] = add_strong_account.region

        else:
            # For other database platforms (PostgreSQL, MySQL, MariaDB, MSSql, Oracle, Sybase)
            # username is required (already validated), other fields are optional
            if add_strong_account.address:
                properties['address'] = add_strong_account.address
            if add_strong_account.port:
                properties['port'] = add_strong_account.port
            if add_strong_account.database:
                properties['database'] = add_strong_account.database
            if add_strong_account.dsn:
                properties['dsn'] = add_strong_account.dsn
            # MSSql specific field
            if platform == 'MSSql' and add_strong_account.reconcile_is_win_account is not None:
                properties['reconcileIsWinAccount'] = add_strong_account.reconcile_is_win_account

        return properties

    def _build_password_secret_object(self, add_strong_account: ArkSIADBAddStrongAccount, platform: str) -> dict:
        """Build password secret object based on platform."""
        if platform == 'AWSAccessKeys':
            if not add_strong_account.secret_access_key or not add_strong_account.secret_access_key.get_secret_value():
                raise ArkServiceException('AWSAccessKeys account requires "secret_access_key" field')
            return {'secretAccessKey': add_strong_account.secret_access_key.get_secret_value()}
        else:
            if not add_strong_account.password or not add_strong_account.password.get_secret_value():
                raise ArkServiceException(f'{platform} account requires "password" field with non-empty value')
            return {'password': add_strong_account.password.get_secret_value()}

    def update_strong_account(self, update_strong_account: ArkSIADBUpdateStrongAccount) -> ArkSIADBStrongAccountMetadata:
        """
        Updates a managed DB strong account.

        Note: Only managed accounts can be updated, PAM accounts cannot be updated.

        Args:
            update_strong_account: Update request with account details

        Returns:
            ArkSIADBStrongAccountMetadata: Updated account metadata

        Raises:
            ArkServiceException: If validation fails or API request fails
        """
        self._logger.info(f'Updating db strong account with id [{update_strong_account.strong_account_id}]')

        # Build the update payload
        request_payload = self._build_update_account_request(update_strong_account)
        self._logger.debug(f'Update payload: {request_payload}')

        # Backend uses PUT method, not PATCH
        resp: Response = self.__client.put(
            STRONG_ACCOUNT_ROUTE.format(strong_account_id=update_strong_account.strong_account_id),
            json=request_payload,
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBStrongAccountMetadata.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update strong account response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update strong account response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update strong account [{resp.text}] - [{resp.status_code}]')

    def _build_update_account_request(self, update_account: ArkSIADBUpdateStrongAccount) -> dict:
        """Build update request payload for managed account."""
        platform = update_account.platform
        account_properties = self._build_account_properties(update_account, platform)

        payload = {
            'store_type': 'managed',
            'name': update_account.name,
            'account_properties': account_properties,
        }

        # Add optional password_secret_object if provided
        if update_account.password or update_account.secret_access_key:
            payload['password_secret_object'] = self._build_password_secret_object(update_account, platform)

        return payload

    def delete_strong_account(self, delete_strong_account: ArkSIADBDeleteStrongAccount) -> None:
        """
        Deletes a DB strong account.

        Args:
            delete_strong_account (ArkSIADBDeleteStrongAccount): Request with account_id

        Raises:
            ArkServiceException: If the request fails or response cannot be parsed
        """
        self._logger.info(f'Deleting db strong account by id [{delete_strong_account.strong_account_id}]')
        resp: Response = self.__client.delete(STRONG_ACCOUNT_ROUTE.format(strong_account_id=delete_strong_account.strong_account_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete db strong account [{resp.text}] - [{resp.status_code}]')

    def list_strong_accounts(self) -> Iterator[ArkSIADBStrongAccountsPage]:
        """
        Lists all database strong accounts with automatic pagination, yielding in pages.

        This method returns an iterator that yields pages of strong accounts as they are fetched.
        Similar to Go's channel-based approach, this allows for streaming results without
        loading all accounts into memory at once.

        Yields:
            Iterator[ArkSIADBStrongAccountsPage]: Pages of strong accounts

        Raises:
            ArkServiceException: If the request fails or response cannot be parsed
        """
        self._logger.info('Listing all db strong accounts (with automatic pagination)')

        next_cursor: Optional[str] = None
        limit = 500  # Default limit, handled internally

        while True:
            params: dict = {'limit': limit}
            if next_cursor:
                params['cursor'] = next_cursor

            self._logger.info('Fetching db strong accounts')
            resp: Response = self.__client.get(STRONG_ACCOUNTS_ROUTE, params=params)

            if resp.status_code != HTTPStatus.OK:
                self._logger.error(f'Failed to fetch db strong accounts - [{resp.status_code}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to fetch db strong accounts [{resp.text}] - [{resp.status_code}]')

            try:
                page_response = ArkSIADBListStrongAccountsResponse.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to decode response: [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to decode response: [{str(ex)}]') from ex

            yield ArkSIADBStrongAccountsPage(page_response.items)

            if not page_response.next_cursor:
                self._logger.info('Retrieved all db strong accounts')
                break

            next_cursor = page_response.next_cursor

    def list_strong_accounts_by(self, strong_accounts_filter: ArkSIADBStrongAccountsFilter) -> Iterator[ArkSIADBStrongAccountsPage]:
        """
        Lists database strong accounts filtered by the given criteria (client-side filtering), yielding in pages.

        This method returns an iterator that yields filtered pages of strong accounts.
        Similar to Go's channel-based approach, filtering is applied on each page as it's received.

        Args:
            strong_accounts_filter: Filter criteria (store_type, platform, name regex pattern)

        Yields:
            Iterator[ArkSIADBStrongAccountsPage]: Filtered pages of strong accounts (only non-empty pages are yielded)

        Raises:
            ArkServiceException: If filter validation fails or request fails
        """
        self._logger.info(f'Listing db strong accounts with filter [{strong_accounts_filter}]')

        if strong_accounts_filter.name:
            try:
                re.compile(strong_accounts_filter.name)
            except re.error as e:
                raise ArkServiceException(f"Invalid name regex pattern '{strong_accounts_filter.name}': {e}") from e

        all_pages = self.list_strong_accounts()

        for page in all_pages:
            filtered_items: List[ArkSIADBStrongAccountMetadata] = []

            for account in page.items:
                if strong_accounts_filter.store_type and account.store_type != strong_accounts_filter.store_type:
                    continue
                if strong_accounts_filter.platform:
                    account_platform = account.account_properties.get('platform')
                    if account_platform != strong_accounts_filter.platform:
                        continue
                if strong_accounts_filter.name:
                    try:
                        if not re.match(strong_accounts_filter.name, account.name):
                            continue
                    except re.error:
                        continue

                filtered_items.append(account)

            if filtered_items:
                yield ArkSIADBStrongAccountsPage(filtered_items)

    def get_strong_account(self, get_strong_account: ArkSIADBGetStrongAccount) -> ArkSIADBStrongAccountMetadata:
        """
        Retrieves a DB strong account.

        Args:
            get_strong_account (ArkSIADBGetStrongAccount): Request with account_id

        Raises:
            ArkServiceException: If the request fails or response cannot be parsed

        Returns:
            ArkSIADBStrongAccountMetadata: The strong account metadata
        """
        self._logger.info(f'Retrieving db strong account by id [{get_strong_account.strong_account_id}]')
        resp: Response = self.__client.get(STRONG_ACCOUNT_ROUTE.format(strong_account_id=get_strong_account.strong_account_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIADBStrongAccountMetadata.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse db strong account response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse db strong account response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve db strong account [{resp.text}] - [{resp.status_code}]')

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
