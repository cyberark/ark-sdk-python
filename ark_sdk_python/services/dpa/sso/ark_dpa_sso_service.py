# pylint: disable=too-many-function-args
import base64
import os
import zipfile
from datetime import datetime
from http import HTTPStatus
from io import BytesIO
from typing import Any, Dict, Final, Optional

from dateutil.parser import parse
from jose.jwt import get_unverified_claims
from overrides import overrides
from requests import Response

from ark_sdk_python.args import ArkArgsFormatter
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkKeyring
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkProfileLoader, ArkServiceException
from ark_sdk_python.models.auth import ArkToken, ArkTokenType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.sso import (
    ArkDPASSOAcquireTokenResponse,
    ArkDPASSOGetShortLivedClientCertificate,
    ArkDPASSOGetShortLivedOracleWallet,
    ArkDPASSOGetShortLivedPassword,
    ArkDPASSOGetShortLivedRDPFile,
    ArkDPASSOShortLivedOracleWalletType,
)
from ark_sdk_python.models.services.dpa.sso.ark_dpa_sso_get_short_lived_client_certificate import ArkDPASSOShortLiveClientCertificateFormat
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-sso', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
ACQUIRE_SSO_TOKEN_URL: Final[str] = '/api/adb/sso/acquire'


class ArkDPASSOService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')
        self.__cache_keyring = ArkKeyring(self.service_config().service_name)

    def __load_from_cache(self, token_type: str) -> Optional[ArkDPASSOAcquireTokenResponse]:
        claims = get_unverified_claims(self.__client.session_token)
        token = self.__cache_keyring.load_token(
            ArkProfileLoader.load_default_profile(),
            postfix=f'{claims["tenant_id"]}_{claims["unique_name"]}_dpa_sso_short_lived_{token_type}',
        )
        if token:
            return ArkDPASSOAcquireTokenResponse.parse_raw(token.token.get_secret_value())
        return None

    def __save_to_cache(self, result: ArkDPASSOAcquireTokenResponse, token_type: str) -> None:
        claims = get_unverified_claims(self.__client.session_token)
        expires_in = datetime.now() + (parse(result.metadata['expires_at']) - parse(result.metadata['created_at']))
        self.__cache_keyring.save_token(
            ArkProfileLoader.load_default_profile(),
            ArkToken(
                token=result.json(),
                token_type=ArkTokenType.Token,
                expires_in=expires_in,
            ),
            postfix=f'{claims["tenant_id"]}_{claims["unique_name"]}_dpa_sso_short_lived_{token_type}',
        )

    def __expand_folder(self, folder: str) -> str:
        folder_path = os.path.expanduser(folder)
        if not folder_path.endswith('/'):
            folder_path += '/'
        return folder_path

    def __output_client_certificate(
        self, folder: str, output_format: ArkDPASSOShortLiveClientCertificateFormat, result: ArkDPASSOAcquireTokenResponse
    ) -> None:
        folder_path = self.__expand_folder(folder)
        claims = get_unverified_claims(self.__client.session_token)
        base_name = claims["unique_name"].split('@')[0]
        client_certificate = result.token['client_certificate']
        private_key = result.token['private_key']

        if output_format == ArkDPASSOShortLiveClientCertificateFormat.RAW:
            ArkArgsFormatter.print_normal(f'client-certificate-data: {client_certificate}')
            ArkArgsFormatter.print_normal(f'client-key-data: {private_key}')
        elif output_format == ArkDPASSOShortLiveClientCertificateFormat.BASE64:
            ArkArgsFormatter.print_normal(
                f'client-certificate-data: {base64.b64encode(client_certificate.encode("utf-8")).decode("utf-8")}'
            )
            ArkArgsFormatter.print_normal(f'client-key-data: {base64.b64encode(private_key.encode("utf-8")).decode("utf-8")}')
        elif output_format == ArkDPASSOShortLiveClientCertificateFormat.FILE:
            if not folder_path:
                raise ArkServiceException(
                    f'Folder parameter is required if format is {ArkDPASSOShortLiveClientCertificateFormat.FILE.value}'
                )
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(f'{folder_path}{os.path.sep}{base_name}_client_cert.crt', 'w', encoding='utf-8') as file_handle:
                file_handle.write(client_certificate)
            with open(f'{folder_path}{os.path.sep}{base_name}_client_key.pem', 'w', encoding='utf-8') as file_handle:
                file_handle.write(private_key)
        elif output_format == ArkDPASSOShortLiveClientCertificateFormat.SINGLE_FILE:
            if not folder:
                raise ArkServiceException(
                    f'Folder parameter is required if format is {ArkDPASSOShortLiveClientCertificateFormat.FILE.value}'
                )
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(f'{folder_path}{os.path.sep}{base_name}_client_cert.pem', 'w', encoding='utf-8') as file_handle:
                file_handle.write(client_certificate)
                file_handle.write('\n')
                file_handle.write(private_key)
        else:
            raise ArkServiceException(f'Unknown format {output_format}')

    def __save_oracle_sso_wallet(self, folder: str, unzip_wallet: bool, result: ArkDPASSOAcquireTokenResponse) -> None:
        folder_path = self.__expand_folder(folder)
        result.token['wallet'] = base64.b64decode(result.token['wallet'])
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if not unzip_wallet:
            claims = get_unverified_claims(self.__client.session_token)
            base_name = claims["unique_name"].split('@')[0]
            with open(f'{folder_path}{os.path.sep}{base_name}_wallet.zip', 'wb') as file_handle:
                file_handle.write(result.token['wallet'])
        else:
            wallet_bytes = BytesIO(result.token['wallet'])
            with zipfile.ZipFile(wallet_bytes, 'r') as zipf:
                zipf.extractall(folder_path)

    def __save_oracle_pem_wallet(self, folder: str, result: ArkDPASSOAcquireTokenResponse) -> None:
        folder_path = self.__expand_folder(folder)
        claims = get_unverified_claims(self.__client.session_token)
        base_name = claims["unique_name"].split('@')[0]
        pem_wallet = base64.b64decode(result.token['pem_wallet']).decode('utf-8')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(f'{folder_path}{os.path.sep}{base_name}_ewallet.pem', 'w', encoding='utf-8') as file_handle:
            file_handle.write(pem_wallet)

    def __save_rdp_file(self, get_short_lived_rdp_file: ArkDPASSOGetShortLivedRDPFile, result: ArkDPASSOAcquireTokenResponse) -> None:
        folder_path = self.__expand_folder(get_short_lived_rdp_file.folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename: str = f'dpa _a {get_short_lived_rdp_file.target_address}'
        if get_short_lived_rdp_file.target_domain:
            filename += f' _d {get_short_lived_rdp_file.target_domain}'
        with open(f'{folder_path}{filename}.rdp', 'w', encoding='utf-8') as file_handle:
            file_handle.write(result.token['text'])

    def short_lived_password(self, get_short_lived_password: ArkDPASSOGetShortLivedPassword) -> str:
        """
        Generates a short-lived password used to connect to DPA services.

        Args:
            get_short_lived_password (ArkDPASSOGetShortLivedPassword): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: __description__
        """
        self._logger.info('Generating short lived password token')
        if get_short_lived_password.allow_caching:
            result = self.__load_from_cache('password')
            if result:
                return result.token['key']
        response: Response = self.__client.post(
            ACQUIRE_SSO_TOKEN_URL,
            json={
                'token_type': 'password',
                'service': 'DPA-DB',
            },
        )
        if response.status_code != HTTPStatus.CREATED:
            raise ArkServiceException(f'Failed to generate short lived password - [{response.status_code}] - [{response.text}]')
        result: ArkDPASSOAcquireTokenResponse = ArkDPASSOAcquireTokenResponse.parse_obj(response.json())
        if 'key' in result.token:
            if get_short_lived_password.allow_caching:
                self.__save_to_cache(result, 'password')
            return result.token['key']
        raise ArkServiceException(f'Failed to generate short lived password - [{response.status_code}] - [{response.text}]')

    def short_lived_client_certificate(self, get_short_lived_client_certificate: ArkDPASSOGetShortLivedClientCertificate) -> None:
        """
        Generates a short-lived client certificate used to connect to DPA services.

        Args:
            get_short_lived_client_certificate (ArkDPASSOGetShortLivedClientCertificate): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: __description__
        """
        self._logger.info('Generating short lived client certificate')
        if get_short_lived_client_certificate.allow_caching:
            result = self.__load_from_cache('client_certificate')
            if result:
                self.__output_client_certificate(
                    get_short_lived_client_certificate.folder, get_short_lived_client_certificate.output_format, result
                )
                return
        response: Response = self.__client.post(
            ACQUIRE_SSO_TOKEN_URL,
            json={
                'token_type': 'client_certificate',
                'service': get_short_lived_client_certificate.service,
            },
        )
        if response.status_code != HTTPStatus.CREATED:
            raise ArkServiceException(f'Failed to generate short lived client certificate - [{response.status_code}] - [{response.text}]')
        result: ArkDPASSOAcquireTokenResponse = ArkDPASSOAcquireTokenResponse.parse_obj(response.json())
        if 'client_certificate' in result.token and 'private_key' in result.token:
            if get_short_lived_client_certificate.allow_caching:
                self.__save_to_cache(result, 'client_certificate')
            self.__output_client_certificate(
                get_short_lived_client_certificate.folder, get_short_lived_client_certificate.output_format, result
            )
            return
        raise ArkServiceException(f'Failed to generate short lived password - [{response.status_code}] - [{response.text}]')

    def short_lived_oracle_wallet(self, get_short_lived_oracle_wallet: ArkDPASSOGetShortLivedOracleWallet) -> None:
        """
        Generates a short-lived Oracle Wallet used to connect via DPA to Oracle databases.

        Args:
            get_short_lived_oracle_wallet (ArkDPASSOGetShortLivedOracleWallet): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: __description__
        """
        self._logger.info('Generating short lived oracle wallet')
        if get_short_lived_oracle_wallet.allow_caching:
            result = self.__load_from_cache('oracle_wallet')
            if result:
                if get_short_lived_oracle_wallet.wallet_type == ArkDPASSOShortLivedOracleWalletType.SSO:
                    self.__save_oracle_sso_wallet(get_short_lived_oracle_wallet.folder, get_short_lived_oracle_wallet.unzip_wallet, result)
                if get_short_lived_oracle_wallet.wallet_type == ArkDPASSOShortLivedOracleWalletType.PEM:
                    self.__save_oracle_pem_wallet(get_short_lived_oracle_wallet.folder, get_short_lived_oracle_wallet.unzip_wallet, result)
                return
        response: Response = self.__client.post(
            ACQUIRE_SSO_TOKEN_URL,
            json={
                'token_type': 'oracle_wallet',
                'service': 'DPA-DB',
                'token_parameters': {
                    'walletType': get_short_lived_oracle_wallet.wallet_type.value,
                },
            },
        )
        if response.status_code != HTTPStatus.CREATED:
            raise ArkServiceException(f'Failed to generate short lived oracle wallet - [{response.status_code}] - [{response.text}]')
        result: ArkDPASSOAcquireTokenResponse = ArkDPASSOAcquireTokenResponse.parse_obj(response.json())
        if 'wallet' in result.token and get_short_lived_oracle_wallet.wallet_type == ArkDPASSOShortLivedOracleWalletType.SSO:
            if get_short_lived_oracle_wallet.allow_caching:
                self.__save_to_cache(result, 'oracle_wallet')
            self.__save_oracle_sso_wallet(get_short_lived_oracle_wallet.folder, get_short_lived_oracle_wallet.unzip_wallet, result)
            return
        elif 'pem_wallet' in result.token and get_short_lived_oracle_wallet.wallet_type == ArkDPASSOShortLivedOracleWalletType.PEM:
            if get_short_lived_oracle_wallet.allow_caching:
                self.__save_to_cache(result, 'oracle_wallet')
            self.__save_oracle_pem_wallet(get_short_lived_oracle_wallet.folder, result)
            return
        raise ArkServiceException(f'Failed to generate short lived password - [{response.status_code}] - [{response.text}]')

    def short_lived_rdp_file(self, get_short_lived_rdp_file: ArkDPASSOGetShortLivedRDPFile) -> None:
        """
        Generates a short-lived RDP file used to connect via RDP to Windows machines.

        Args:
            get_short_lived_rdp_file (ArkDPASSOGetShortLivedRDPFile): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: __description__
        """
        self._logger.info('Generating short lived rdp file')
        if get_short_lived_rdp_file.allow_caching:
            result = self.__load_from_cache('rdp_file')
            if result:
                self.__save_rdp_file(get_short_lived_rdp_file, result)
        token_parameters: Dict[str, Any] = {
            'targetAddress': get_short_lived_rdp_file.target_address,
            'targetDomain': get_short_lived_rdp_file.target_domain,
            'targetUser': get_short_lived_rdp_file.target_user,
            'elevatedPrivileges': get_short_lived_rdp_file.elevated_privileges,
        }
        response: Response = self.__client.post(
            ACQUIRE_SSO_TOKEN_URL,
            json={
                'token_type': 'rdp_file',
                'service': 'DPA-RDP',
                'token_parameters': {k: v for k, v in token_parameters.items() if v is not None},
                'token_response_format': 'extended',
            },
        )
        if response.status_code != HTTPStatus.CREATED:
            raise ArkServiceException(f'Failed to generate short lived rdp file - [{response.status_code}] - [{response.text}]')
        result: ArkDPASSOAcquireTokenResponse = ArkDPASSOAcquireTokenResponse.parse_obj(response.json())
        if 'text' in result.token:
            if get_short_lived_rdp_file.allow_caching:
                self.__save_to_cache(result, 'rdp_file')
            self.__save_rdp_file(get_short_lived_rdp_file, result)
            return
        raise ArkServiceException(f'Failed to generate short rdp file - [{response.status_code}] - [{response.text}]')

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
