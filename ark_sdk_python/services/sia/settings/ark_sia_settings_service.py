from http import HTTPStatus
from json import JSONDecodeError
from typing import Dict, Final

from overrides import overrides
from pydantic import ValidationError
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.settings import (
    ArkSIASettings,
    ArkSIASettingsADBMfaCaching,
    ArkSIASettingsCertificateValidation,
    ArkSIASettingsFeatureName,
    ArkSIASettingsGetSetting,
    ArkSIASettingsK8SMfaCaching,
    ArkSIASettingsListSettings,
    ArkSIASettingsLogonSequence,
    ArkSIASettingsRDPFileTransfer,
    ArkSIASettingsRDPKeyboardLayout,
    ArkSIASettingsRDPMfaCaching,
    ArkSIASettingsRDPRecording,
    ArkSIASettingsRDPTokenMfaCaching,
    ArkSIASettingsSetSetting,
    ArkSIASettingsSetSettings,
    ArkSIASettingsSettingTypes,
    ArkSIASettingsSSHCommandAudit,
    ArkSIASettingsSSHMfaCaching,
    ArkSIASettingsStandingAccess,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-settings', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

SETTINGS_PATH: Final[str] = '/api/settings'
SETTING_PATH: Final[str] = '/api/settings/{feature_name}'

FEATURE_NAME_TO_SETTING: Final[Dict[ArkSIASettingsFeatureName, ArkSIASettingsSettingTypes]] = {
    ArkSIASettingsFeatureName.ADBMfaCaching: ArkSIASettingsADBMfaCaching,
    ArkSIASettingsFeatureName.CertificateValidation: ArkSIASettingsCertificateValidation,
    ArkSIASettingsFeatureName.K8SMfaCaching: ArkSIASettingsK8SMfaCaching,
    ArkSIASettingsFeatureName.RDPFileTransfer: ArkSIASettingsRDPFileTransfer,
    ArkSIASettingsFeatureName.RDPKeyboardLayout: ArkSIASettingsRDPKeyboardLayout,
    ArkSIASettingsFeatureName.RDPMfaCaching: ArkSIASettingsRDPMfaCaching,
    ArkSIASettingsFeatureName.RDPRecording: ArkSIASettingsRDPRecording,
    ArkSIASettingsFeatureName.RDPTokenMfaCaching: ArkSIASettingsRDPTokenMfaCaching,
    ArkSIASettingsFeatureName.SSHMfaCaching: ArkSIASettingsSSHMfaCaching,
    ArkSIASettingsFeatureName.SSHCommandAudit: ArkSIASettingsSSHCommandAudit,
    ArkSIASettingsFeatureName.StandingAccess: ArkSIASettingsStandingAccess,
    ArkSIASettingsFeatureName.LogonSequence: ArkSIASettingsLogonSequence,
}


class ArkSIASettingsService(ArkService):
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

    def setting(self, get_setting: ArkSIASettingsGetSetting) -> ArkSIASettingsSettingTypes:
        """
        Get SIA setting.

        Args:
            get_setting (ArkSIASettingsGetSetting): The setting to get.

        Raises:
            ArkServiceException: If an error occurs while getting the settings.

        Returns:
            ArkSIASettings: The retrieved SIA settings.
        """
        self._logger.info('Getting SIA settings')
        response: Response = self.__client.get(SETTING_PATH.format(feature_name=get_setting.feature_name.value))
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to get SIA settings - [{response.status_code}] - [{response.text}]')
        try:
            return FEATURE_NAME_TO_SETTING[get_setting.feature_name].model_validate(response.json()['feature_conf'])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse get settings response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse get settings response [{str(ex)}]') from ex

    def set_setting(self, set_setting: ArkSIASettingsSetSetting) -> ArkSIASettingsSettingTypes:
        """
        Set SIA settings.

        Args:
            set_setting (ArkSIASettingsSetSetting): The new SIA setting.

        Raises:
            ArkServiceException: If there is an error setting the SIA setting.

        Returns:
            ArkSIASettings: The new SIA setting.
        """
        self._logger.info(f'Setting SIA setting [{set_setting.feature_name}]')
        response: Response = self.__client.put(
            SETTING_PATH.format(feature_name=set_setting.feature_name.value),
            json=set_setting.setting.model_dump(exclude_none=True, by_alias=True),
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to set SIA setting - [{response.status_code}] - [{response.text}]')
        return set_setting.setting

    def list_settings(self, list_settings: ArkSIASettingsListSettings) -> ArkSIASettings:
        """
        Get SIA settings.

        Args:
            list_settings (ArkSIASettingsListSettings): The settings to list.

        Raises:
            ArkServiceException: If an error occurs while getting the settings.

        Returns:
            ArkSIASettings: The retrieved SIA settings.
        """
        self._logger.info('Getting SIA settings')
        response: Response = self.__client.get(SETTINGS_PATH, params=list_settings.model_dump())
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to get SIA settings - [{response.status_code}] - [{response.text}]')
        try:
            return ArkSIASettings.model_validate_json(response.text)
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse get settings response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse get settings response [{str(ex)}]') from ex

    def set_settings(self, set_settings: ArkSIASettingsSetSettings) -> ArkSIASettings:
        """
        Set SIA settings.

        Args:
            set_settings (ArkSIASettingsSetSettings): The new SIA settings.

        Raises:
            ArkServiceException: If there is an error setting the SIA settings.

        Returns:
            ArkSIASettings: The new SIA settings.
        """
        self._logger.info('Setting SIA settings')
        response: Response = self.__client.patch(SETTINGS_PATH, json=set_settings.model_dump(exclude_none=True, by_alias=True))
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to set SIA settings - [{response.status_code}] - [{response.text}]')
        return self.list_settings(ArkSIASettingsListSettings())

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
