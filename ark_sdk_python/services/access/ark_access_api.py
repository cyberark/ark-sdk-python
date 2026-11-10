from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.services.access.assets import ArkAccessAssetsService


class ArkAccessAPI:
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        self.__assets_service = ArkAccessAssetsService(isp_auth)

    @property
    def assets(self) -> ArkAccessAssetsService:
        """
        Getter for the access assets service.

        Returns:
            ArkAccessAssetsService: Access assets service.
        """
        return self.__assets_service
