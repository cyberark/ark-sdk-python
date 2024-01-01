from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.services.dpa.certificates import ArkDPACertificatesService
from ark_sdk_python.services.dpa.db import ArkDPADBService
from ark_sdk_python.services.dpa.k8s import ArkDPAK8SService
from ark_sdk_python.services.dpa.policies.db import ArkDPADBPoliciesService
from ark_sdk_python.services.dpa.policies.vm import ArkDPAVMPoliciesService
from ark_sdk_python.services.dpa.secrets.db import ArkDPADBSecretsService
from ark_sdk_python.services.dpa.sso import ArkDPASSOService
from ark_sdk_python.services.dpa.workspaces.db import ArkDPADBWorkspaceService


class ArkDPAAPI:
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        self.__db_workspace_service = ArkDPADBWorkspaceService(isp_auth)
        self.__vm_policies_service = ArkDPAVMPoliciesService(isp_auth)
        self.__db_policies_service = ArkDPADBPoliciesService(isp_auth)
        self.__db_secrets_service = ArkDPADBSecretsService(isp_auth)
        self.__sso_service = ArkDPASSOService(isp_auth)
        self.__db_service = ArkDPADBService(isp_auth)
        self.__certificates_service = ArkDPACertificatesService(isp_auth)
        self.__k8s_service = ArkDPAK8SService(isp_auth)

    @property
    def workspace_db(self) -> ArkDPADBWorkspaceService:
        """
        Getter for the DB workspace service.

        Returns:
            ArkDPADBWorkspaceService: _description_
        """
        return self.__db_workspace_service

    @property
    def policies_vm(self) -> ArkDPAVMPoliciesService:
        """
        Getter for the VM policies service.

        Returns:
            ArkDPAVMPoliciesService: _description_
        """
        return self.__vm_policies_service

    @property
    def policies_db(self) -> ArkDPADBPoliciesService:
        """
        Getter for the DB policies service.

        Returns:
            ArkDPADBPoliciesService: _description_
        """
        return self.__db_policies_service

    @property
    def secrets_db(self) -> ArkDPADBSecretsService:
        """
        Getter for the DB secrets service.

        Returns:
            ArkDPADBSecretsService: _description_
        """
        return self.__db_secrets_service

    @property
    def sso(self) -> ArkDPASSOService:
        """
        Getter for the SSO service.

        Returns:
            ArkDPASSOService: _description_
        """
        return self.__sso_service

    @property
    def db(self) -> ArkDPADBService:
        """
        Getter for the DB service.

        Returns:
            ArkDPADBService: _description_
        """
        return self.__db_service

    @property
    def certificates(self) -> ArkDPACertificatesService:
        """
        Getter for the certificates service.

        Returns:
            ArkDPACertificatesService: _description_
        """
        return self.__certificates_service

    @property
    def k8s(self) -> ArkDPAK8SService:
        """
        Getter for the K8s service.

        Returns:
            ArkDPAK8SService: _description_
        """
        return self.__k8s_service
