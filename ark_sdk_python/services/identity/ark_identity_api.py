from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.services.identity.connectors import ArkIdentityConnectorsService
from ark_sdk_python.services.identity.directories import ArkIdentityDirectoriesService
from ark_sdk_python.services.identity.policies import ArkIdentityPoliciesService
from ark_sdk_python.services.identity.roles import ArkIdentityRolesService
from ark_sdk_python.services.identity.users import ArkIdentityUsersService


class ArkIdentityAPI:
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        self.__identity_connectors = ArkIdentityConnectorsService(isp_auth)
        self.__identity_directories = ArkIdentityDirectoriesService(isp_auth)
        self.__identity_policies = ArkIdentityPoliciesService(isp_auth)
        self.__identity_roles = ArkIdentityRolesService(isp_auth)
        self.__identity_users = ArkIdentityUsersService(isp_auth)

    @property
    def identity_connectors(self) -> ArkIdentityConnectorsService:
        """
        Getter for the identity connectors service

        Returns:
            ArkIdentityConnectorsService: _description_
        """
        return self.__identity_connectors

    @property
    def identity_directories(self) -> ArkIdentityDirectoriesService:
        """
        Getter for the identity directories service

        Returns:
            ArkIdentityDirectoriesService: _description_
        """
        return self.__identity_directories

    @property
    def identity_policies(self) -> ArkIdentityPoliciesService:
        """
        Getter for the identity policies service

        Returns:
            ArkIdentityPoliciesService: _description_
        """
        return self.__identity_policies

    @property
    def identity_roles(self) -> ArkIdentityRolesService:
        """
        Getter for the identity roles service

        Returns:
            ArkIdentityRolesService: _description_
        """
        return self.__identity_roles

    @property
    def identity_users(self) -> ArkIdentityUsersService:
        """
        Getter for the identity users service

        Returns:
            ArkIdentityUsersService: _description_
        """
        return self.__identity_users
