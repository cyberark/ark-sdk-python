import json
import os
from http import HTTPStatus
from typing import Final, Optional

from overrides import overrides
from requests import Response

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.k8s import (
    ArkSIAK8SClusters,
    ArkSIAK8SGenerateClusterConfig,
    ArkSIAK8SGenerateKubeConfig,
    ArkSIAK8SListClusters,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-k8s', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
BUILD_KUBE_CONFIG_PATH: Final[str] = '/api/k8s/kube-config'
CLUSTERS_PATH: Final[str] = '/api/k8s/clusters'
GENERATE_CLUSTER_CONFIG_PATH: Final[str] = '/api/k8s/clusters/generate'


class ArkSIAK8SService(ArkService):
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

    @staticmethod
    def _save_kube_config_file(folder: str, result: str) -> None:
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(f'{folder}{os.path.sep}config', 'w', encoding='utf-8') as file_handle:
            file_handle.write(result)

    @staticmethod
    def _save_clusters_file(output_file: str, clusters: ArkSIAK8SClusters) -> None:
        folder = os.path.dirname(output_file)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        clusters_data = clusters.model_dump(mode='json', by_alias=True, exclude_none=True)
        # Add an empty "reason" placeholder for clusters that require one, so the saved file is ready to be
        # filled in and used as-is with `generate_cluster_config`
        for cluster, cluster_data in zip(clusters.clusters, clusters_data['clusters']):
            if cluster.is_reason_required and 'reason' not in cluster_data:
                cluster_data['reason'] = ''
        with open(output_file, 'w', encoding='utf-8') as file_handle:
            json.dump(clusters_data, file_handle, indent=2)

    def generate_kubeconfig(self, generate_kubeconfig: ArkSIAK8SGenerateKubeConfig) -> Optional[str]:
        """
        Builds a Kube config file used to connect to a K8s cluster

        Args:
            generate_kubeconfig (ArkSIAK8SGenerateKubeConfig): _description_

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
            ArkSIAK8SService._save_kube_config_file(generate_kubeconfig.folder, result)
            return None
        return result

    def list_clusters(self, list_clusters: Optional[ArkSIAK8SListClusters] = None) -> ArkSIAK8SClusters:
        """
        Lists the K8s clusters that are available for the current user to access

        Args:
            list_clusters (Optional[ArkSIAK8SListClusters], optional): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkSIAK8SClusters: _description_
        """
        self._logger.info('Listing k8s clusters')
        response: Response = self.__client.get(CLUSTERS_PATH)
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to list k8s clusters - [{response.status_code}] - [{response.text}]')
        clusters = ArkSIAK8SClusters.model_validate(response.json())
        if list_clusters and list_clusters.output_file:
            ArkSIAK8SService._save_clusters_file(list_clusters.output_file, clusters)
        return clusters

    def generate_cluster_config(self, generate_cluster_config: ArkSIAK8SGenerateClusterConfig) -> Optional[str]:
        """
        Generates a kube config file for the given clusters, using the access reasons supplied in the given clusters file.
        The clusters file is expected to be in the same format as the one returned/saved by `list_clusters`, with an
        additional "reason" field filled in per cluster where a reason is required (`isReasonRequired` is `true`).

        Args:
            generate_cluster_config (ArkSIAK8SGenerateClusterConfig): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            Optional[str]: _description_
        """
        if not os.path.isfile(generate_cluster_config.clusters_file):
            raise ArkServiceException(f'Clusters file [{generate_cluster_config.clusters_file}] does not exist')
        with open(generate_cluster_config.clusters_file, 'r', encoding='utf-8') as file_handle:
            clusters_data = json.load(file_handle)
        clusters = ArkSIAK8SClusters.model_validate(clusters_data)
        self._logger.info('Generating kube config file for the given clusters and reasons')
        response: Response = self.__client.post(
            GENERATE_CLUSTER_CONFIG_PATH, json=clusters.model_dump(mode='json', by_alias=True, exclude_none=True)
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to generate k8s cluster config - [{response.status_code}] - [{response.text}]')
        result = response.text
        if generate_cluster_config.folder:
            ArkSIAK8SService._save_kube_config_file(generate_cluster_config.folder, result)
            return None
        return result

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
