import os
import subprocess
from typing import Final

from jose.jwt import get_unverified_claims
from overrides import overrides

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.databases import ArkDPADatabasesPsqlExecution
from ark_sdk_python.models.services.dpa.sso import ArkDPASSOGetShortLivedPassword
from ark_sdk_python.services.ark_service import ArkService
from ark_sdk_python.services.dpa.sso.ark_dpa_sso_service import ArkDPASSOService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-databases', required_authenticator_names=['isp'], optional_authenticator_names=[]
)


class ArkDPADatabasesService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__sso_service = ArkDPASSOService(self.__isp_auth)

    def __proxy_address(self, db_type: str):
        claims = get_unverified_claims(self.__isp_auth.token.token.get_secret_value())
        return f'{claims["subdomain"]}.{db_type}.{claims["platform_domain"]}'

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

    def psql(self, psql_execution: ArkDPADatabasesPsqlExecution) -> None:
        """
        Exectues psql command line for postgres via CyberArk's Database Proxy

        Args:
            psql_execution (ArkDPADatabasesPsqlExecution): _description_

        Raises:
            ArkServiceException: _description_
        """
        claims = get_unverified_claims(self.__isp_auth.token.token.get_secret_value())
        proxy_address = self.__proxy_address("postgres")
        # Standing
        if psql_execution.target_username:
            username_connection_string = f'{claims["unique_name"]}@{psql_execution.target_username}@{psql_execution.target_address}'
        # Dynamic
        else:
            username_connection_string = f'{claims["unique_name"]}@{psql_execution.target_address}'
        password = self.__sso_service.short_lived_password(ArkDPASSOGetShortLivedPassword())
        execution_action = f'{psql_execution.psql_path} "host={proxy_address} user={username_connection_string}"'
        self.__add_to_pgpass(username_connection_string, proxy_address, password)
        try:
            self.__execute(execution_action)
        finally:
            self.__remove_from_pgpass(username_connection_string, proxy_address, password)

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
