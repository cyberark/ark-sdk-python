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
    def identity_directories(self) -> "ArkIdentityDirectoriesService":
        """
        Returns the Identity Directories Service if the appropriate authenticators were given

        Returns:
            ArkIdentityDirectoriesService: _description_
        """
        from ark_sdk_python.services.identity.directories import ArkIdentityDirectoriesService

        return cast(ArkIdentityDirectoriesService, self.service(ArkIdentityDirectoriesService))

    @property
    def identity_policies(self) -> "ArkIdentityPoliciesService":
        """
        Returns the Identity Policies Service if the appropriate authenticators were given

        Returns:
            ArkIdentityPoliciesService: _description_
        """
        from ark_sdk_python.services.identity.policies import ArkIdentityPoliciesService

        return cast(ArkIdentityPoliciesService, self.service(ArkIdentityPoliciesService))

    @property
    def identity_roles(self) -> "ArkIdentityRolesService":
        """
        Returns the Identity Roles Service if the appropriate authenticators were given

        Returns:
            ArkIdentityRolesService: _description_
        """
        from ark_sdk_python.services.identity.roles import ArkIdentityRolesService

        return cast(ArkIdentityRolesService, self.service(ArkIdentityRolesService))

    @property
    def identity_users(self) -> "ArkIdentityUsersService":
        """
        Returns the Identity Users Service if the appropriate authenticators were given

        Returns:
            ArkIdentityUsersService: _description_
        """
        from ark_sdk_python.services.identity.users import ArkIdentityUsersService

        return cast(ArkIdentityUsersService, self.service(ArkIdentityUsersService))

    @property
    def dpa_workspaces_db(self) -> "ArkDPADBWorkspaceService":
        """
        Returns the DPA DB Workspace service if the appropriate authenticators were provided.

        Returns:
            ArkDPADBWorkspaceService: _description_
        """
        from ark_sdk_python.services.dpa.workspaces.db import ArkDPADBWorkspaceService

        return cast(ArkDPADBWorkspaceService, self.service(ArkDPADBWorkspaceService))

    @property
    def dpa_policies_vm(self) -> "ArkDPAVMPoliciesService":
        """
        Returns the DPA VM Policies service if the appropriate authenticators were provided.

        Returns:
            ArkDPAVMPoliciesService: _description_
        """
        from ark_sdk_python.services.dpa.policies.vm import ArkDPAVMPoliciesService

        return cast(ArkDPAVMPoliciesService, self.service(ArkDPAVMPoliciesService))

    @property
    def dpa_policies_db(self) -> "ArkDPADBPoliciesService":
        """
        Returns the DPA DB Policies service if the appropriate authenticators were provided.

        Returns:
            ArkDPADBPoliciesService: _description_
        """
        from ark_sdk_python.services.dpa.policies.db import ArkDPADBPoliciesService

        return cast(ArkDPADBPoliciesService, self.service(ArkDPADBPoliciesService))

    @property
    def dpa_secrets_db(self) -> "ArkDPADBSecretsService":
        """
        Returns the DPA DB Secrets service if the appropriate authenticators were provided.

        Returns:
            ArkDPADBSecretsService: _description_
        """
        from ark_sdk_python.services.dpa.secrets.db import ArkDPADBSecretsService

        return cast(ArkDPADBSecretsService, self.service(ArkDPADBSecretsService))

    @property
    def dpa_sso(self) -> "ArkDPASSOService":
        """
        Returns the DPA sso service if the appropriate authenticators were provided.

        Returns:
            ArkDPASSOService: _description_
        """
        from ark_sdk_python.services.dpa.sso import ArkDPASSOService

        return cast(ArkDPASSOService, self.service(ArkDPASSOService))

    @property
    def dpa_db(self) -> "ArkDPADBService":
        """
        Returns the DPA DB service if the appropriate authenticators were provided.

        Returns:
            ArkDPADBService: _description_
        """
        from ark_sdk_python.services.dpa.db import ArkDPADBService

        return cast(ArkDPADBService, self.service(ArkDPADBService))

    @property
    def dpa_certificates(self) -> "ArkDPACertificatesService":
        """
        Returns DPA certificates service if the appropriate authenticators were provided.

        Returns:
            ArkDPACertificatesService: _description_
        """
        from ark_sdk_python.services.dpa.certificates import ArkDPACertificatesService

        return cast(ArkDPACertificatesService, self.service(ArkDPACertificatesService))

    @property
    def dpa_k8s(self) -> "ArkDPAK8SService":
        """
        Returns the DPA Policies service if the appropriate authenticators were provided.

        Returns:
            ArkDPAK8SService: _description_
        """
        from ark_sdk_python.services.dpa.k8s import ArkDPAK8SService

        return cast(ArkDPAK8SService, self.service(ArkDPAK8SService))

    @property
    def sm(self) -> "ArkSMService":
        """
        Returns the SM service if the appropriate authenticators were given

        Returns:
            ArkSMService: _description_
        """
        from ark_sdk_python.services.sm import ArkSMService

        return cast(ArkSMService, self.service(ArkSMService))
