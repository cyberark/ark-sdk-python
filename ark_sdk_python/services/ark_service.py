from abc import ABC, abstractmethod
from typing import Any, List

from ark_sdk_python.auth.ark_auth import ArkAuth
from ark_sdk_python.common import get_logger
from ark_sdk_python.models import ArkNotFoundException, ArkValidationException
from ark_sdk_python.models.services import ArkServiceConfig


class ArkService(ABC):
    def __init__(self, *authenticators: Any) -> None:
        self._logger = get_logger(self.__class__.__name__)
        self._authenticators = [auth for auth in authenticators if issubclass(type(auth), ArkAuth)]
        given_auth_names = [auth.authenticator_name() for auth in self._authenticators]
        if any(a not in given_auth_names for a in self.service_config().required_authenticator_names):
            raise ArkValidationException(f'{self.service_config().service_name} missing required authenticators for service')

    @property
    def authenticators(self) -> List[ArkAuth]:
        """
        Returns all the authenticators for the service.

        Returns:
            List[ArkAuth]: _description_
        """
        return self._authenticators

    def authenticator(self, auth_name: str) -> ArkAuth:
        """
        Finds the appropriate Ark authenticator class for the specified authenticator.

        Args:
            auth_name (str): _description_

        Raises:
            ArkNotFoundException: _description_

        Returns:
            ArkAuth: _description_
        """
        for auth in self.authenticators:
            if auth.authenticator_name() == auth_name:
                return auth
        raise ArkNotFoundException(f'{self.service_config().service_name} Failed to find authenticator {auth_name}')

    def has_authenticator(self, auth_name: str) -> bool:
        """
        Checks whether the specified authenticator name exists.

        Args:
            auth_name (str): _description_

        Returns:
            bool: _description_
        """
        return any(auth.authenticator_name() == auth_name for auth in self.authenticators)

    @staticmethod
    @abstractmethod
    def service_config() -> ArkServiceConfig:
        """
        Returns the service configuration, which includes the service name, and its required and optional authenticators.

        Returns:
            ArkServiceConfig: _description_
        """
