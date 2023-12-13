---
title: Adding a New Authenticator
description: Adding a New Authenticator
---

# Adding a New Authenticator
To add a new authenticator, one must implement the following interface [ark_auth.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/auth/ark_auth.py){:target="_blank" rel="noopener"}:

```python
class ArkAuth(ABC):
    @abstractmethod
    def _perform_authentication(
        self, profile: ArkProfile, auth_profile: ArkAuthProfile, secret: Optional[ArkSecret] = None, force: bool = False
    ) -> ArkToken:
        """
        Performs the actual authentication, based on the implementation

        Args:
            profile (ArkProfile): Profile to authenticate on
            auth_profile (ArkAuthProfile): Specific auth profile for the authentication
            secret (Optional[ArkSecret]): Secret used for authentication. Defaults to None
            force (bool): Force authenticate and ignore caching

        Returns:
            Optional[ArkToken]: Token of the authentication to be used
        """

    @staticmethod
    @abstractmethod
    def authenticator_name() -> str:
        """
        Name of the authenticator to be used for the auth profiles and services

        Returns:
            str: _description_
        """

    @staticmethod
    @abstractmethod
    def authenticator_human_readable_name() -> str:
        """
        Human readable name of the authenticator to be used for representation to the user

        Returns:
            str: _description_
        """

    @staticmethod
    @abstractmethod
    def supported_auth_methods() -> List[ArkAuthMethod]:
        """
        Supported authenticaton methods by this authenticator

        Returns:
            List[ArkAuthMethod]: _description_
        """

    @staticmethod
    @abstractmethod
    def default_auth_method() -> Tuple[ArkAuthMethod, ArkAuthMethodSettings]:
        """
        Default authentication method used by this authenticator with its default settings

        Returns:
            Tuple[ArkAuthMethod, ArkAuthMethodSettings]: _description_
        """
```

The above will implement the authenticator logic itself, and all needed information about the authenticator

Once implemented, you may use it accordingly with the fitting services who need such authenticator

If you also wish to expose the authenticator to the CLI, u may also add him to the SUPPORTED_AUTHENTICATORS list under [auth/__init__.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/auth/__init__.py){:target="_blank" rel="noopener"}:

Once added, it will be automatically exposed on configure and login actions
