from http import HTTPStatus
from json import JSONDecodeError
from typing import Final

import pyperclip
from overrides import overrides
from pydantic import ValidationError
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.access.assets import (
    ArkAccessAssetsAssets,
    ArkAccessAssetsListAssets,
    ArkAccessAssetsSecretRequest,
    ArkAccessAssetsSecretResponse,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='access-assets', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

LIST_ASSETS_PATH: Final[str] = '/api/assets'
GET_SECRET_PATH: Final[str] = '/api/assets/{assetId}/secret'


class ArkAccessAssetsService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='userportal',
            seperator='-',
            refresh_connection_callback=self.__refresh_access_auth,
        )

    def __refresh_access_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    def list(self, assets_query: ArkAccessAssetsListAssets) -> ArkAccessAssetsAssets:
        """
        List access assets.

        :param assets_query: Instance of ArkAccessAssetsListAssets containing key-value query parameters.
        :return: Instance of ArkAccessAssetsAssets containing the list of assets.
        :raises ArkServiceException: If the request fails or the response cannot be parsed.
        """
        self._logger.info('Getting access assets')
        response: Response = self.__client.get(LIST_ASSETS_PATH, params=assets_query.model_dump())
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to get access assets - [{response.status_code}] - [{response.text}]')
        try:
            return ArkAccessAssetsAssets.model_validate_json(response.text)
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse access assets response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse access assets response [{str(ex)}]') from ex

    def secret(self, secret_request: ArkAccessAssetsSecretRequest) -> ArkAccessAssetsSecretResponse:
        """
        Get the secret for an access asset.

        :param secret_request: Instance of ArkAccessAssetsSecretRequest containing the asset ID and reason.
        :return: Instance of ArkAccessAssetsSecretResponse and copies the secret to the clipboard.
        :raises ArkServiceException: If the request fails or the response cannot be parsed.
        """
        self._logger.info('Get access asset secret')
        response: Response = self.__client.post(
            GET_SECRET_PATH.format(assetId=secret_request.asset_id),
            json={'reason': secret_request.reason} if secret_request.reason else {},
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to get access asset secret - [{response.status_code}] - [{response.text}]')
        try:
            validated_response = ArkAccessAssetsSecretResponse.model_validate_json(response.text)
            pyperclip.copy(validated_response.secret)
            validated_response.security_message = (
                'The secret has been copied to your clipboard. Please ensure you delete the secret after use.'
            )
            return validated_response
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse access asset secret response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse access asset secret response [{str(ex)}]') from ex

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
