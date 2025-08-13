from __future__ import annotations

from typing import Dict, List, Optional, Type, cast

from ark_sdk_python.auth.ark_auth import ArkAuth
from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.ark_profile import ArkProfile, ArkProfileLoader
from ark_sdk_python.services.ark_service import ArkService


class ArkAPI:
    def __init__(self, authenticators: List[ArkAuth], profile: Optional[ArkProfile] = None) -> None:
        self.__authenticators = authenticators
        self.__lazy_loaded_services: Dict[str, ArkService] = {}
        self.__profile = profile or ArkProfileLoader.load_default_profile()

    def __lazy_load_service(self, service_type: Type[ArkService]) -> ArkService:
        service_name = service_type.service_config().service_name
        required_auth_names = service_type.service_config().required_authenticator_names
        required_autheneticators = [auth for auth in self.__authenticators if auth.authenticator_name() in required_auth_names]
        optional_authenticators = [
            auth
            for auth in self.__authenticators
            if auth.authenticator_name() in service_type.service_config().optional_authenticator_names
        ]
        if len(required_autheneticators) == len(required_auth_names):
            authenticators = {f'{a.authenticator_name()}_auth': a for a in required_autheneticators + optional_authenticators}
            self.__lazy_loaded_services[service_name] = service_type(**authenticators)
        else:
            raise ArkServiceException(
                f'{service_name.title()} is not supported or missing fitting authenticators, please make sure you are logged in'
            )
        return self.__lazy_loaded_services[service_name]

    def authenticator(self, authenticator_name: str) -> ArkAuth:
        """
        Returns the specified authenticator.

        Args:
            authenticator_name (str): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkAuth: _description_
        """
        for auth in self.__authenticators:
            if auth.authenticator_name() == authenticator_name:
                return auth
        raise ArkServiceException(f'{authenticator_name} is not supported or not found')

    def service(self, service_type: Type[ArkService]) -> ArkService:
        """
        Returns the specified service when the appropriate authenticators were provided.

        Args:
            service_type (Type[ArkService]): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkService: _description_
        """
        if not issubclass(service_type, ArkService):
            raise ArkServiceException(f"Type {service_type} is invalid")
        service_name = service_type.service_config().service_name
        if service_name in self.__lazy_loaded_services:
            return self.__lazy_loaded_services[service_name]
        return self.__lazy_load_service(service_type)

    @property
    def profile(self) -> ArkProfile:
        """
        Gets the API profile

        Returns:
            ArkProfile: _description_
        """
        return self.__profile

    @property
    def identity_connectors(self) -> "ArkIdentityConnectorsService":
        """
        Returns the Identity Connectors Service if the appropriate authenticators were provided.

        Returns:
            ArkIdentityConnectorsService: _description_
        """
        from ark_sdk_python.services.identity.connectors import ArkIdentityConnectorsService

        return cast(ArkIdentityConnectorsService, self.service(ArkIdentityConnectorsService))

    @property
    def identity_directories(self) -> "ArkIdentityDirectoriesService":
        """
        Returns the Identity Directories Service if the appropriate authenticators were provided.

        Returns:
            ArkIdentityDirectoriesService: _description_
        """
        from ark_sdk_python.services.identity.directories import ArkIdentityDirectoriesService

        return cast(ArkIdentityDirectoriesService, self.service(ArkIdentityDirectoriesService))

    @property
    def identity_policies(self) -> "ArkIdentityPoliciesService":
        """
        Returns the Identity Policies Service if the appropriate authenticators were provided.

        Returns:
            ArkIdentityPoliciesService: _description_
        """
        from ark_sdk_python.services.identity.policies import ArkIdentityPoliciesService

        return cast(ArkIdentityPoliciesService, self.service(ArkIdentityPoliciesService))

    @property
    def identity_roles(self) -> "ArkIdentityRolesService":
        """
        Returns the Identity Roles Service if the appropriate authenticators were provided.

        Returns:
            ArkIdentityRolesService: _description_
        """
        from ark_sdk_python.services.identity.roles import ArkIdentityRolesService

        return cast(ArkIdentityRolesService, self.service(ArkIdentityRolesService))

    @property
    def identity_users(self) -> "ArkIdentityUsersService":
        """
        Returns the Identity Users Service if the appropriate authenticators were provided.

        Returns:
            ArkIdentityUsersService: _description_
        """
        from ark_sdk_python.services.identity.users import ArkIdentityUsersService

        return cast(ArkIdentityUsersService, self.service(ArkIdentityUsersService))

    @property
    def sm(self) -> "ArkSMService":
        """
        Returns the Session Monitoring service if the appropriate authenticators were provided.

        Returns:
            ArkSMService: _description_
        """
        from ark_sdk_python.services.sm import ArkSMService

        return cast(ArkSMService, self.service(ArkSMService))

    @property
    def sia_workspaces_target_sets(self) -> "ArkSIATargetSetsWorkspaceService":
        """
        Returns the SIA Target Sets Workspace service if the appropriate authenticators were provided.

        Returns:
            ArkSIATargetSetsWorkspaceService: _description_
        """
        from ark_sdk_python.services.sia.workspaces.targetsets import ArkSIATargetSetsWorkspaceService

        return cast(ArkSIATargetSetsWorkspaceService, self.service(ArkSIATargetSetsWorkspaceService))

    @property
    def sia_workspaces_db(self) -> "ArkSIADBWorkspaceService":
        """
        Returns the SIA DB Workspace service if the appropriate authenticators were provided.

        Returns:
            ArkSIADBWorkspaceService: _description_
        """
        from ark_sdk_python.services.sia.workspaces.db import ArkSIADBWorkspaceService

        return cast(ArkSIADBWorkspaceService, self.service(ArkSIADBWorkspaceService))

    @property
    def sia_policies_vm(self) -> "ArkSIAVMPoliciesService":
        """
        Returns the SIA VM Policies service if the appropriate authenticators were provided.

        Returns:
            ArkSIAVMPoliciesService: _description_
        """
        from ark_sdk_python.services.sia.policies.vm import ArkSIAVMPoliciesService

        return cast(ArkSIAVMPoliciesService, self.service(ArkSIAVMPoliciesService))

    @property
    def sia_policies_db(self) -> "ArkSIADBPoliciesService":
        """
        Returns the SIA DB Policies service if the appropriate authenticators were provided.

        Returns:
            ArkSIADBPoliciesService: _description_
        """
        from ark_sdk_python.services.sia.policies.db import ArkSIADBPoliciesService

        return cast(ArkSIADBPoliciesService, self.service(ArkSIADBPoliciesService))

    @property
    def sia_secrets_vm(self) -> "ArkSIAVMSecretsService":
        """
        Returns the SIA VM Secrets service if the appropriate authenticators were provided.

        Returns:
            ArkSIAVMSecretsService: _description_
        """
        from ark_sdk_python.services.sia.secrets.vm import ArkSIAVMSecretsService

        return cast(ArkSIAVMSecretsService, self.service(ArkSIAVMSecretsService))

    @property
    def sia_secrets_db(self) -> "ArkSIADBSecretsService":
        """
        Returns the SIA DB Secrets service if the appropriate authenticators were provided.

        Returns:
            ArkSIADBSecretsService: _description_
        """
        from ark_sdk_python.services.sia.secrets.db import ArkSIADBSecretsService

        return cast(ArkSIADBSecretsService, self.service(ArkSIADBSecretsService))

    @property
    def sia_access(self) -> "ArkSIAAccessService":
        """
        Returns the SIA Access service if the appropriate authenticators were provided.

        Returns:
            ArkSIAAccessService: _description_
        """
        from ark_sdk_python.services.sia.access import ArkSIAAccessService

        return cast(ArkSIAAccessService, self.service(ArkSIAAccessService))

    @property
    def sia_ssh_ca(self) -> "ArkSIASSHCAService":
        """
        Returns the SIA SSH CA service if the appropriate authenticators were provided.

        Returns:
            ArkSIASSHCAService: _description_
        """
        from ark_sdk_python.services.sia.ssh_ca import ArkSIASSHCAService

        return cast(ArkSIASSHCAService, self.service(ArkSIASSHCAService))

    @property
    def sia_sso(self) -> "ArkSIASSOService":
        """
        Returns the SIA sso service if the appropriate authenticators were provided.

        Returns:
            ArkSIASSOService: _description_
        """
        from ark_sdk_python.services.sia.sso import ArkSIASSOService

        return cast(ArkSIASSOService, self.service(ArkSIASSOService))

    @property
    def sia_db(self) -> "ArkSIADBService":
        """
        Returns the SIA DB service if the appropriate authenticators were provided.

        Returns:
            ArkSIADBService: _description_
        """
        from ark_sdk_python.services.sia.db import ArkSIADBService

        return cast(ArkSIADBService, self.service(ArkSIADBService))

    @property
    def sia_certificates(self) -> "ArkSIACertificatesService":
        """
        Returns SIA certificates service if the appropriate authenticators were provided.

        Returns:
            ArkSIACertificatesService: _description_
        """
        from ark_sdk_python.services.sia.certificates import ArkSIACertificatesService

        return cast(ArkSIACertificatesService, self.service(ArkSIACertificatesService))

    @property
    def sia_k8s(self) -> "ArkSIAK8SService":
        """
        Returns the SIA K8S service if the appropriate authenticators were provided.

        Returns:
            ArkSIAK8SService: _description_
        """
        from ark_sdk_python.services.sia.k8s import ArkSIAK8SService

        return cast(ArkSIAK8SService, self.service(ArkSIAK8SService))

    @property
    def sia_settings(self) -> "ArkSIASettingsService":
        """
        Returns the SIA Settings service if the appropriate authenticators were provided.

        Returns:
            ArkSIASettingsService: _description_
        """
        from ark_sdk_python.services.sia.settings import ArkSIASettingsService

        return cast(ArkSIASettingsService, self.service(ArkSIASettingsService))

    @property
    def pcloud_accounts(self) -> "ArkPCloudAccountsService":
        """
        Returns the PCloud Accounts service if the appropriate authenticators were provided.

        Returns:
            ArkPCloudAccountsService: _description_
        """
        from ark_sdk_python.services.pcloud.accounts import ArkPCloudAccountsService

        return cast(ArkPCloudAccountsService, self.service(ArkPCloudAccountsService))

    @property
    def pcloud_safes(self) -> "ArkPCloudSafesService":
        """
        Returns the PCloud Safes service if the appropriate authenticators were provided.

        Returns:
            ArkPCloudSafesService: _description_
        """
        from ark_sdk_python.services.pcloud.safes import ArkPCloudSafesService

        return cast(ArkPCloudSafesService, self.service(ArkPCloudSafesService))

    @property
    def pcloud_platforms(self) -> "ArkPCloudPlatformsService":
        """
        Returns the PCloud Platforms service if the appropriate authenticators were provided.

        Returns:
            ArkPCloudPlatformsService: _description_
        """
        from ark_sdk_python.services.pcloud.platforms import ArkPCloudPlatformsService

        return cast(ArkPCloudPlatformsService, self.service(ArkPCloudPlatformsService))

    @property
    def pcloud_applications(self) -> "ArkPCloudApplicationsService":
        """
        Returns the PCloud Applications service if the appropriate authenticators were provided.

        Returns:
            ArkPCloudApplicationsService: _description_
        """
        from ark_sdk_python.services.pcloud.applications import ArkPCloudApplicationsService

        return cast(ArkPCloudApplicationsService, self.service(ArkPCloudApplicationsService))

    @property
    def cmgr(self) -> "ArkCmgrService":
        """
        Returns the Connector Management service if the appropriate authenticators were provided.

        Returns:
            ArkCmgrService: _description_
        """
        from ark_sdk_python.services.cmgr import ArkCmgrService

        return cast(ArkCmgrService, self.service(ArkCmgrService))

    @property
    def uap(self) -> "ArkUAPService":
        """
        Returns the UAP Executions service if the appropriate authenticators were provided.

        Returns:
            ArkUAPService: _description_
        """

        from ark_sdk_python.services.uap.ark_uap_service import ArkUAPService

        return cast(ArkUAPService, self.service(ArkUAPService))

    @property
    def uap_sca(self) -> "ArkUAPSCAService":
        """
        Returns the UAP SCA Executions service if the appropriate authenticators were provided.

        Returns:
            ArkUAPSCAService: _description_
        """

        from ark_sdk_python.services.uap.sca.ark_uap_sca_service import ArkUAPSCAService

        return cast(ArkUAPSCAService, self.service(ArkUAPSCAService))

    @property
    def uap_db(self) -> "ArkUAPSIADBService":
        """
        Returns the UAP SIA DB Executions service if the appropriate authenticators were provided.

        Returns:
            ArkUAPSIADBService: _description_
        """

        from ark_sdk_python.services.uap.sia.db.ark_uap_sia_db_service import ArkUAPSIADBService

        return cast(ArkUAPSIADBService, self.service(ArkUAPSIADBService))

    @property
    def uap_vm(self) -> "ArkUAPSIAVMService":
        """
        Returns the UAP SIA VM Executions service if the appropriate authenticators were provided.

        Returns:
            ArkUAPSIAVMService: _description_
        """

        from ark_sdk_python.services.uap.sia.vm.ark_uap_sia_vm_service import ArkUAPSIAVMService

        return cast(ArkUAPSIAVMService, self.service(ArkUAPSIAVMService))
