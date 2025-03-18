import json
from fnmatch import fnmatch
from http import HTTPStatus
from typing import Any, Dict, Final, List, Optional, Set, Union

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.secrets.vm import (
    ArkSIAVMAddSecret,
    ArkSIAVMChangeSecret,
    ArkSIAVMDeleteSecret,
    ArkSIAVMGetSecret,
    ArkSIAVMSecret,
    ArkSIAVMSecretInfo,
    ArkSIAVMSecretsFilter,
    ArkSIAVMSecretsStats,
    ArkSIAVMSecretType,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-secrets-vm', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
SECRETS_ROUTE: Final[str] = 'api/secrets'
SECRET_ROUTE: Final[str] = 'api/secrets/{secret_id}'
SECRET_ACTIONS_ROUTE: Final[str] = 'api/secrets/actions/{action_name}'


class ArkSIAVMSecretsService(ArkService):
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

    def __deduce_secret_data(self, secret_input: Union[ArkSIAVMAddSecret, ArkSIAVMChangeSecret]) -> str:
        # Construct the secret data from the type
        if secret_input.secret_type == ArkSIAVMSecretType.ProvisionerUser:
            if not secret_input.provisioner_username or not secret_input.provisioner_password:
                raise ArkServiceException('Provisioner user secret type requires both the username and the password to be supplied')
            secret_data = json.dumps(
                {'username': secret_input.provisioner_username, 'password': secret_input.provisioner_password.get_secret_value()}
            )
        else:
            if not secret_input.pcloud_account_name or not secret_input.pcloud_account_safe:
                raise ArkServiceException('PCloud account secret type requires both the safe and the account name to be supplied')
            secret_data = json.dumps({'safe': secret_input.pcloud_account_safe, 'account_name': secret_input.pcloud_account_name})
        return secret_data

    def __list_secrets_with_filters(
        self,
        secret_type: Optional[ArkSIAVMSecretType] = ArkSIAVMSecretType.ProvisionerUser,
        secret_details: Optional[Dict[str, Any]] = None,
    ) -> List[ArkSIAVMSecretInfo]:
        params = {'secret_type': ','.join(st for st in ArkSIAVMSecretType)}
        if secret_details:
            params.update(secret_details)
        if secret_type:
            params.update({"secret_type": secret_type.value})
        resp: Response = self.__client.get(SECRETS_ROUTE, params=params)
        if resp.status_code == HTTPStatus.OK:
            try:
                return TypeAdapter(List[ArkSIAVMSecretInfo]).validate_python(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse list secrets response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list secrets response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list secrets [{resp.text}] - [{resp.status_code}]')

    def add_secret(self, add_secret: ArkSIAVMAddSecret) -> ArkSIAVMSecret:
        """
        Adds a new vm secret to the secret store

        Args:
            add_secret (ArkSIAVMAddSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMSecret: _description_
        """
        self._logger.info('Adding new vm secret')
        secret_data = self.__deduce_secret_data(add_secret)
        add_secret.secret_details = add_secret.secret_details or {}
        resp: Response = self.__client.post(
            SECRETS_ROUTE,
            json={
                **add_secret.model_dump(include={'secret_name', 'secret_details', 'secret_type'}),
                'secret': {'secret_data': secret_data, 'tenant_encrypted': False},
                'is_active': not add_secret.is_disabled,
            },
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkSIAVMSecret.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add vm secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add vm secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add vm secret [{resp.text}] - [{resp.status_code}]')

    def change_secret(self, change_secret: ArkSIAVMChangeSecret) -> ArkSIAVMSecret:
        """
        Changes an existing vm secret with either data or metadata

        Args:
            change_secret (ArkSIAVMChangeSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMSecret: _description_
        """
        self._logger.info(f'Changing existing vm secret with id [{change_secret.secret_id}]')
        secret_data = None
        try:
            secret_data = self.__deduce_secret_data(change_secret)
        except ArkServiceException:
            pass
        if not secret_data and not change_secret.secret_details and not change_secret.secret_name and change_secret.is_disabled is None:
            raise ArkServiceException('At least one change needs to be supplied')
        resp: Response = self.__client.post(
            SECRET_ROUTE.format(secret_id=change_secret.secret_id),
            json={
                'secret': {'secret_data': secret_data, 'tenant_encrypted': False},
                'secret_details': change_secret.secret_details,
                'is_active': True if change_secret.is_disabled is None or not change_secret.is_disabled else False,
                'secret_name': change_secret.secret_name,
            },
        )
        if resp.status_code == HTTPStatus.OK:
            return self.secret(ArkSIAVMGetSecret(secret_id=change_secret.secret_id))
        raise ArkServiceException(f'Failed to change vm secret [{resp.text}] - [{resp.status_code}]')

    def delete_secret(self, delete_secret: ArkSIAVMDeleteSecret) -> None:
        """
        Deletes a vm secret by id if exists

        Args:
            delete_secret (ArkSIAVMDeleteSecret): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting vm secret by id [{delete_secret.secret_id}]')
        resp: Response = self.__client.delete(SECRET_ROUTE.format(secret_id=delete_secret.secret_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete vm secret [{resp.text}] - [{resp.status_code}]')

    def list_secrets(self) -> List[ArkSIAVMSecretInfo]:
        """
        Lists all tenant vm secrets

        Returns:
            List[ArkSIASecretInfo]: _description_
        """
        self._logger.info('Listing all vm secrets')
        return self.__list_secrets_with_filters()

    def list_secrets_by(self, secrets_filter: ArkSIAVMSecretsFilter) -> List[ArkSIAVMSecretInfo]:
        """
        Lists vm secrets by given filters

        Args:
            secrets_filter (ArkSIASecretsFilter): _description_

        Returns:
            List[ArkSIASecretInfo]: _description_
        """
        self._logger.info(f'Listing vm secrets by filters [{secrets_filter}]')
        secret_type = None
        secret_details = secrets_filter.secret_details
        if secrets_filter.secret_types and len(secrets_filter.secret_types) == 1:
            secret_type = secrets_filter.secret_types[0]
        secrets = self.__list_secrets_with_filters(secret_type, secret_details)

        # Filter by secret types
        if secrets_filter.secret_types and len(secrets_filter.secret_types) > 1:
            secrets = [s for s in secrets if s.secret_type in secrets_filter.secret_types]

        # Filter by name
        if secrets_filter.name:
            secrets = [s for s in secrets if s.secret_name and fnmatch(s.secret_name, secrets_filter.name)]

        # Filter by is active
        if secrets_filter.is_active is not None:
            secrets = [s for s in secrets if s.is_active == secrets_filter.is_active]

        return secrets

    def secret(self, get_secret: ArkSIAVMGetSecret) -> ArkSIAVMSecret:
        """
        Retrieves a vm secret by id

        Args:
            get_secret (ArkSIAVMGetSecret): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAVMSecret: _description_
        """
        self._logger.info(f'Retrieving vm secret by id [{get_secret.secret_id}]')
        resp: Response = self.__client.get(SECRET_ROUTE.format(secret_id=get_secret.secret_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkSIAVMSecret.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse vm secret response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse vm secret response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve vm secret [{resp.text}] - [{resp.status_code}]')

    def secrets_stats(self) -> ArkSIAVMSecretsStats:
        """
        Calculates vm secrets statistics

        Returns:
            ArkSIAVMSecretsStats: _description_
        """
        self._logger.info('Calculating vm secrets statistics')
        secrets = self.list_secrets()
        secrets_stats = ArkSIAVMSecretsStats.model_construct()
        secrets_stats.secrets_count = len(secrets)
        secrets_stats.active_secrets_count = len([s for s in secrets if s.is_active])
        secrets_stats.inactive_secrets_count = len([s for s in secrets if not s.is_active])

        # Count secrets per type
        secret_types: Set[ArkSIAVMSecretType] = {s.secret_type for s in secrets if s.secret_type}
        secrets_stats.secrets_count_by_type = {
            st: len([s for s in secrets if s.secret_type and s.secret_type == st]) for st in secret_types
        }

        return secrets_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
