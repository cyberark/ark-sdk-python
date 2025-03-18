from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.services.pcloud.accounts import ArkPCloudAccountsService
from ark_sdk_python.services.pcloud.applications import ArkPCloudApplicationsService
from ark_sdk_python.services.pcloud.platforms import ArkPCloudPlatformsService
from ark_sdk_python.services.pcloud.safes import ArkPCloudSafesService


class ArkPCloudAPI:
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        self.__accounts_service = ArkPCloudAccountsService(isp_auth)
        self.__platforms_service = ArkPCloudPlatformsService(isp_auth)
        self.__safes_service = ArkPCloudSafesService(isp_auth)
        self.__applications_service = ArkPCloudApplicationsService(isp_auth)

    @property
    def accounts(self) -> ArkPCloudAccountsService:
        """
        Getter for the accounts service

        Returns:
            ArkPCloudAccountsService: _description_
        """
        return self.__accounts_service

    @property
    def platforms(self) -> ArkPCloudPlatformsService:
        """
        Getter for the platforms service

        Returns:
            ArkPCloudPlatformsService: _description_
        """
        return self.__platforms_service

    @property
    def safes(self) -> ArkPCloudSafesService:
        """
        Getter for the safes service

        Returns:
            ArkPCloudSafesService: _description_
        """
        return self.__safes_service

    @property
    def applications(self) -> ArkPCloudApplicationsService:
        """
        Getter for the applications service

        Returns:
            ArkPCloudApplicationsService: _description_
        """
        return self.__applications_service
