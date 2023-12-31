import os
from http import HTTPStatus
from typing import Final, Optional

from overrides import overrides
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.k8s import ArkDPAK8SGenerateKubeConfig
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-k8s', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
BUILD_KUBE_CONFIG_PATH: Final[str] = '/api/k8s/kube-config'


class ArkDPAK8SService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')

    @staticmethod
    def _save_kube_config_file(folder: str, result: str) -> None:
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(f'{folder}{os.path.sep}config', 'w', encoding='utf-8') as file_handle:
            file_handle.write(result)

    def generate_kubeconfig(self, generate_kubeconfig: ArkDPAK8SGenerateKubeConfig) -> Optional[str]:
        """
        Builds a Kube config file used to connect to a K8s cluster.

        Args:
            generate_kubeconfig (ArkDPAK8SGenerateKubeConfig): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            str: __description__
        """
        self._logger.info('Building kube config file')
        response: Response = self.__client.get(BUILD_KUBE_CONFIG_PATH)
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to build kube config file - [{response.status_code}] - [{response.text}]')
        result = response.text
        if generate_kubeconfig.folder:
            ArkDPAK8SService._save_kube_config_file(generate_kubeconfig.folder, result)
            return None
        return result

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
