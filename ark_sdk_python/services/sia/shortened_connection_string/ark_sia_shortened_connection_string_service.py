from http import HTTPStatus
from json import JSONDecodeError
from typing import Final

from overrides import overrides
from pydantic import ValidationError
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.shortened_connection_string import (
    ArkSIAGenerateShortenedConnectionString,
    ArkSIAGenerateShortenedConnectionStringResponse,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-shortened-connection-string', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
GENERATE_SHORTENED_CONNECTION_STRING_API: Final[str] = 'api/guidance/aliases'


class ArkSIAShortenedConnectionStringService(ArkService):
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

    def generate(self, generate_shortened_connection_string: ArkSIAGenerateShortenedConnectionString) -> str:
        """
        Generates a shortened connection string for the given raw_connection_string.

        Args:
            generate_shortened_connection_string (ArkSIAGenerateShortenedConnectionString): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: The generated shortened connection string.
        """
        self._logger.info('Generating shortened connection string')
        body = {
            'raw_connection_string': generate_shortened_connection_string.raw_connection_string,
        }
        response: Response = self.__client.post(
            GENERATE_SHORTENED_CONNECTION_STRING_API,
            json=body,
        )
        # Validate the response
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to generate shortened connection string [{response.text}] - [{response.status_code}]')

        try:
            result: ArkSIAGenerateShortenedConnectionStringResponse = ArkSIAGenerateShortenedConnectionStringResponse.model_validate(
                response.json()
            )
        except (ValidationError, JSONDecodeError) as ex:
            self._logger.exception(f'Failed to generate shortened connection string [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to generate shortened connection string [{str(ex)}]') from ex
        return result.shortened_connection_string

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
