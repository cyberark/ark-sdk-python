from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.services.sia.access import ArkSIAAccessService
from ark_sdk_python.services.sia.certificates import ArkSIACertificatesService
from ark_sdk_python.services.sia.db import ArkSIADBService
from ark_sdk_python.services.sia.k8s import ArkSIAK8SService
from ark_sdk_python.services.sia.policies.db import ArkSIADBPoliciesService
from ark_sdk_python.services.sia.policies.vm import ArkSIAVMPoliciesService
from ark_sdk_python.services.sia.secrets.db import ArkSIADBSecretsService
from ark_sdk_python.services.sia.secrets.vm import ArkSIAVMSecretsService
from ark_sdk_python.services.sia.ssh_ca import ArkSIASSHCAService
from ark_sdk_python.services.sia.sso import ArkSIASSOService
from ark_sdk_python.services.sia.workspaces.db import ArkSIADBWorkspaceService
from ark_sdk_python.services.sia.workspaces.targetsets import ArkSIATargetSetsWorkspaceService


class ArkSIAAPI:
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        self.__db_workspace_service = ArkSIADBWorkspaceService(isp_auth)
        self.__targetsets_workspace_service = ArkSIATargetSetsWorkspaceService(isp_auth)
        self.__vm_policies_service = ArkSIAVMPoliciesService(isp_auth)
        self.__db_policies_service = ArkSIADBPoliciesService(isp_auth)
        self.__db_secrets_service = ArkSIADBSecretsService(isp_auth)
        self.__vm_secrets_service = ArkSIAVMSecretsService(isp_auth)
        self.__sso_service = ArkSIASSOService(isp_auth)
        self.__db_service = ArkSIADBService(isp_auth)
        self.__certificates_service = ArkSIACertificatesService(isp_auth)
        self.__k8s_service = ArkSIAK8SService(isp_auth)
        self.__access_service = ArkSIAAccessService(isp_auth)
        self.__ssh_ca_service = ArkSIASSHCAService(isp_auth)

    @property
    def workspace_db(self) -> ArkSIADBWorkspaceService:
        """
        Getter for the DB workspace service.

        Returns:
            ArkSIADBWorkspaceService: _description_
        """
        return self.__db_workspace_service

    @property
    def workspace_target_sets(self) -> ArkSIATargetSetsWorkspaceService:
        """
        Getter for the Target Sets workspace service.

        Returns:
            ArkSIATargetSetsWorkspaceService: _description_
        """
        return self.__targetsets_workspace_service

    @property
    def access(self) -> ArkSIAAccessService:
        """
        Getter for the Access service

        Returns:
            ArkSIAAccessService: _description_
        """
        return self.__access_service

    @property
    def policies_vm(self) -> ArkSIAVMPoliciesService:
        """
        Getter for the VM policies service.

        Returns:
            ArkSIAVMPoliciesService: _description_
        """
        return self.__vm_policies_service

    @property
    def policies_db(self) -> ArkSIADBPoliciesService:
        """
        Getter for the DB policies service.

        Returns:
            ArkSIADBPoliciesService: _description_
        """
        return self.__db_policies_service

    @property
    def secrets_db(self) -> ArkSIADBSecretsService:
        """
        Getter for the DB secrets service.

        Returns:
            ArkSIADBSecretsService: _description_
        """
        return self.__db_secrets_service

    @property
    def secrets_vm(self) -> ArkSIADBSecretsService:
        """
        Getter for the VM secrets service.

        Returns:
            ArkSIAVMSecretsService: _description_
        """
        return self.__vm_secrets_service

    @property
    def sso(self) -> ArkSIASSOService:
        """
        Getter for the SSO service.

        Returns:
            ArkSIASSOService: _description_
        """
        return self.__sso_service

    @property
    def db(self) -> ArkSIADBService:
        """
        Getter for the DB service.

        Returns:
            ArkSIADBService: _description_
        """
        return self.__db_service

    @property
    def certificates(self) -> ArkSIACertificatesService:
        """
        Getter for the certificates service.

        Returns:
            ArkSIACertificatesService: _description_
        """
        return self.__certificates_service

    @property
    def k8s(self) -> ArkSIAK8SService:
        """
        Getter for the K8s service.

        Returns:
            ArkSIAK8SService: _description_
        """
        return self.__k8s_service

    @property
    def ssh_ca(self) -> ArkSIASSHCAService:
        """
        Getter for the SSH CA service

        Returns:
            ArkDPASSHCAService: _description_
        """
        return self.__ssh_ca_service
