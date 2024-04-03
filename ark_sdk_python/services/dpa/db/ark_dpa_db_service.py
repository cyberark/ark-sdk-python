import base64
import os
import subprocess
import tempfile
import zipfile
from http import HTTPStatus
from io import BytesIO
from json import JSONDecodeError
from typing import Any, Dict, Final, Optional

from jose.jwt import get_unverified_claims
from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import running_os
from ark_sdk_python.models.common.ark_connection_method import ArkConnectionMethod
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.db import (
    ArkDPADBAssetsResponseFormat,
    ArkDPADBAssetsType,
    ArkDPADBGeneratedAssets,
    ArkDPADBMysqlExecution,
    ArkDPADBOracleGenerateAssets,
    ArkDPADBProxyFullchainGenerateAssets,
    ArkDPADBPsqlExecution,
)
from ark_sdk_python.models.services.dpa.sso import ArkDPASSOGetShortLivedPassword
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import ArkDPADBDatabaseFamilyType
from ark_sdk_python.services.ark_service import ArkService
from ark_sdk_python.services.dpa.sso.ark_dpa_sso_service import ArkDPASSOService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-db', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
ASSETS_API: Final[str] = 'api/adb/guidance/generate'


class ArkDPADBService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__sso_service = ArkDPASSOService(self.__isp_auth)
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')

    def __proxy_address(self, db_type: str):
        claims = get_unverified_claims(self.__isp_auth.token.token.get_secret_value())
        return f'{claims["subdomain"]}.{db_type}.{claims["platform_domain"]}'

    def __connection_string(self, target_address: str, target_username: Optional[str] = None) -> None:
        claims = get_unverified_claims(self.__isp_auth.token.token.get_secret_value())
        if target_username:
            # Standing
            return f'{claims["unique_name"]}@{target_username}@{target_address}'
        # Dynamic
        return f'{claims["unique_name"]}@{target_address}'

    def __create_mylogin_cnf(self, username: str, address: str, password: str) -> str:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        temp_file.write('[client]\n' f'user = {username}\n' f'password = {password}\n' f'host = {address}\n')
        temp_file.close()
        os.chmod(temp_file.name, 0o600)
        return temp_file.name

    def __add_to_pgpass(self, username: str, address: str, password: str) -> None:
        pass_format = f'{address}:*:*:{username}:{password}'
        flags = 'r+'
        change_chomd = False
        path = f'{os.path.expanduser("~")}{os.path.sep}.pgpass'
        if not os.path.exists(path):
            flags = 'w+'
            change_chomd = True
        with open(path, flags, encoding='utf-8') as pg_file_handler:
            lines = pg_file_handler.readlines()
            for line in lines:
                if line == pass_format:
                    return
            lines.append(pass_format)
            pg_file_handler.seek(0)
            pg_file_handler.truncate()
            pg_file_handler.writelines(lines)
        if change_chomd:
            os.chmod(path, 0o600)

    def __remove_from_pgpass(self, username: str, address: str, password: str) -> None:
        pass_format = f'{address}:*:*:{username}:{password}'
        if not os.path.exists(f'{os.path.expanduser("~")}{os.path.sep}.pgpass'):
            return
        with open(f'{os.path.expanduser("~")}{os.path.sep}.pgpass', 'r+', encoding='utf-8') as pg_file_handler:
            lines = pg_file_handler.readlines()
            updated_lines = []
            for line in lines:
                if line == pass_format:
                    continue
                updated_lines.append(line)
            pg_file_handler.seek(0)
            pg_file_handler.truncate()
            pg_file_handler.writelines(updated_lines)

    def __execute(self, command_line: str) -> None:
        p = subprocess.Popen(command_line, shell=True)
        p.communicate()

    def psql(self, psql_execution: ArkDPADBPsqlExecution) -> None:
        """
        Executes a Postgres psql command via CyberArk's Database Proxy.

        Args:
            psql_execution (ArkDPADBPsqlExecution): _description_

        Raises:
            ArkServiceException: _description_
        """
        proxy_address = self.__proxy_address("postgres")
        connection_string = self.__connection_string(psql_execution.target_address, psql_execution.target_username)
        password = self.__sso_service.short_lived_password(ArkDPASSOGetShortLivedPassword())
        execution_action = f'{psql_execution.psql_path} "host={proxy_address} user={connection_string}"'
        self.__add_to_pgpass(connection_string, proxy_address, password)
        try:
            self.__execute(execution_action)
        finally:
            self.__remove_from_pgpass(connection_string, proxy_address, password)

    def mysql(self, mysql_execution: ArkDPADBMysqlExecution) -> None:
        """
        Executes a MySQL command line via CyberArk's Database Proxy.

        Args:
            mysql_execution (ArkDPADBMysqlExecution): _description_

        Raises:
            ArkServiceException: _description_
        """
        proxy_address = self.__proxy_address("mysql")
        connection_string = self.__connection_string(mysql_execution.target_address, mysql_execution.target_username)
        password = self.__sso_service.short_lived_password(ArkDPASSOGetShortLivedPassword())
        temp_cnf_login = self.__create_mylogin_cnf(connection_string, proxy_address, password)
        execution_action = f'{mysql_execution.mysql_path} --defaults-file={temp_cnf_login}'
        try:
            self.__execute(execution_action)
        finally:
            os.unlink(temp_cnf_login)

    def __generate_assets(
        self,
        asset_type: ArkDPADBAssetsType,
        connection_method: ArkConnectionMethod,
        response_format: ArkDPADBAssetsResponseFormat,
        generation_hints: Optional[Dict[str, Any]] = None,
        include_sso: Optional[bool] = None,
        resource_type: Optional[ArkDPADBDatabaseFamilyType] = None,
    ) -> ArkDPADBGeneratedAssets:
        body = {
            'asset_type': asset_type,
            'os_type': running_os().value,
            'connection_method': connection_method.value,
            'response_format': response_format.value,
        }
        if generation_hints:
            body['generation_hints'] = generation_hints
        if include_sso is not None:
            body['include_sso'] = include_sso
        if resource_type:
            body['resource_type'] = resource_type.value
        resp: Response = self.__client.post(
            ASSETS_API,
            json=body,
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                if response_format == ArkDPADBAssetsResponseFormat.RAW:
                    return resp.text
                return ArkDPADBGeneratedAssets.parse_obj(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to generate assets [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to generate assets [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to generate assets [{resp.text}] - [{resp.status_code}]')

    def generate_oracle_tnsnames(self, generate_oracle_assets: ArkDPADBOracleGenerateAssets) -> None:
        """
        Generates an Oracle `tnsnames` file and, optionally, an Oracle Wallet (if permitted).

        Args:
            generate_oracle_assets (ArkDPADBOracleGenerateAssets): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info('Generating oracle tns names')
        assets_data = self.__generate_assets(
            asset_type=ArkDPADBAssetsType.OracleTNSAssets,
            connection_method=generate_oracle_assets.connection_method,
            response_format=generate_oracle_assets.response_format,
            generation_hints={'folder': generate_oracle_assets.folder},
            include_sso=generate_oracle_assets.include_sso,
            resource_type=ArkDPADBDatabaseFamilyType.Oracle,
        )
        if isinstance(assets_data, ArkDPADBGeneratedAssets):
            assets_data = assets_data.assets['generated_assets']
        assets_data = base64.b64decode(assets_data)
        if not os.path.exists(generate_oracle_assets.folder):
            os.makedirs(generate_oracle_assets.folder)
        if not generate_oracle_assets.unzip:
            with open(f'{generate_oracle_assets.folder}{os.path.sep}oracle_assets.zip', 'wb') as file_handle:
                file_handle.write(assets_data)
        else:
            assets_bytes = BytesIO(assets_data)
            with zipfile.ZipFile(assets_bytes, 'r') as zipf:
                zipf.extractall(generate_oracle_assets.folder)

    def generate_proxy_fullchain(self, generate_proxy_fullchain: ArkDPADBProxyFullchainGenerateAssets) -> None:
        """
        Generates the proxy fullchain certificates for full certificate validation.

        Args:
            generate_proxy_fullchain (ArkDPADBProxyFullchainGenerateAssets): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info('Generating proxy fullchain')
        assets_data = self.__generate_assets(
            asset_type=ArkDPADBAssetsType.ProxyFullChain,
            connection_method=generate_proxy_fullchain.connection_method,
            response_format=generate_proxy_fullchain.response_format,
        )
        if isinstance(assets_data, ArkDPADBGeneratedAssets):
            assets_data = assets_data.assets['generated_assets']
        if not os.path.exists(generate_proxy_fullchain.folder):
            os.makedirs(generate_proxy_fullchain.folder)
        with open(f'{generate_proxy_fullchain.folder}{os.path.sep}proxy_fullchain.pem', 'w', encoding='utf-8') as file_handle:
            file_handle.write(assets_data)

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
