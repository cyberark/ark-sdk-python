import os
from http import HTTPStatus
from typing import Final

from overrides import overrides
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.ssh_ca import ArkSIAGetSSHPublicKey
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-ssh-ca', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

# SSH CA Key Rotation
GENERATE_NEW_CA_KEY_API: Final[str] = 'api/public-keys/rotation/generate-new'
DEACTIVATE_PREVIOUS_CA_KEY_API: Final[str] = 'api/public-keys/rotation/deactivate-previous'
REACTIVATE_PREVIOUS_CA_KEY_API: Final[str] = 'api/public-keys/rotation/reactivate-previous'

PUBLIC_KEYS_API: Final[str] = 'api/public-keys'
PUBLIC_KEYS_SCRIPT_API: Final[str] = 'api/public-keys/scripts'


class ArkSIASSHCAService(ArkService):
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

    def generate_new_ca(self) -> None:
        """
        Generate new SSH CA key version

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info('Generate new CA key version')
        resp: Response = self.__client.post(GENERATE_NEW_CA_KEY_API)
        if resp.status_code != HTTPStatus.CREATED:
            raise ArkServiceException(f'Failed to generate new CA key [{resp.text}] - [{resp.status_code}]')

    def deactivate_previous_ca(self) -> None:
        """
        Deactivate previous SSH CA key version

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info('Deactivate previous CA key version')
        resp: Response = self.__client.post(DEACTIVATE_PREVIOUS_CA_KEY_API)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to deactivate previous CA key [{resp.text}] - [{resp.status_code}]')

    def reactivate_previous_ca(self) -> None:
        """
        Reactivate previous SSH CA key version

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info('Reactivate previous CA key version')
        resp: Response = self.__client.post(REACTIVATE_PREVIOUS_CA_KEY_API)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to reactivate previous CA key [{resp.text}] - [{resp.status_code}]')

    def public_key(self, get_public_key: ArkSIAGetSSHPublicKey) -> str:
        """
        Retrieves the public key used for SIA SSH connections trust with customer env

        Args:
            get_public_key (ArkSIAGetSSHPublicKey): _description_

        Raises:
            ArkNotSupportedException: _description_
            ArkServiceException: _description_

        Returns:
            str
        """
        self._logger.info('Getting public key')
        resp: Response = self.__client.get(PUBLIC_KEYS_API)
        if resp.status_code == HTTPStatus.OK:
            if get_public_key.output_file:
                os.makedirs(os.path.dirname(get_public_key.output_file), exist_ok=True)
                with open(get_public_key.output_file, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
            return resp.text
        raise ArkServiceException(f'Failed to get public key [{resp.text}] - [{resp.status_code}]')

    def public_key_script(self, get_public_key: ArkSIAGetSSHPublicKey) -> str:
        """
        Retrieves the public key script used for SIA SSH connections trust with customer env
        The script can be run to install the public key in needed ssh configuration files

        Args:
            get_public_key (ArkSIAGetSSHPublicKey): _description_

        Raises:
            ArkNotSupportedException: _description_
            ArkServiceException: _description_

        Returns:
            str
        """
        self._logger.info('Getting public key script')
        resp: Response = self.__client.get(
            PUBLIC_KEYS_SCRIPT_API,
        )
        if resp.status_code == HTTPStatus.OK:
            if get_public_key.output_file:
                os.makedirs(os.path.dirname(get_public_key.output_file), exist_ok=True)
                with open(get_public_key.output_file, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
            return resp.text
        raise ArkServiceException(f'Failed to get public key script [{resp.text}] - [{resp.status_code}]')

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
