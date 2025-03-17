from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, cast
from urllib.parse import urlparse

from ark_sdk_python.common import ArkKeyring, get_logger
from ark_sdk_python.common.ark_keyring import DEFAULT_EXPIRATION_GRACE_DELTA_SECONDS
from ark_sdk_python.models import ArkAuthException, ArkProfile, ArkProfileLoader
from ark_sdk_python.models.auth import (
    ArkAuthMethod,
    ArkAuthMethodSettings,
    ArkAuthMethodsRequireCredentials,
    ArkAuthProfile,
    ArkSecret,
    ArkToken,
    DirectArkAuthMethodSettings,
)


class ArkAuth(ABC):
    def __init__(self, cache_authentication: bool = True, token: Optional[ArkToken] = None) -> None:
        self._logger = get_logger(app=self.__class__.__name__)
        self._cache_authentication = cache_authentication
        self._cache_keyring = None
        if cache_authentication:
            self._cache_keyring = ArkKeyring(self.authenticator_name())
        self.__token = token
        self._active_profile = None
        self._active_auth_profile = None

    def _resolve_cache_postfix(self, auth_profile: ArkAuthProfile) -> str:
        """
        Resolves the postfix used to get the token based on the auth method

        Args:
            auth_profile (ArkAuthProfile): _description_

        Returns:
            str: _description_
        """
        postfix = auth_profile.username
        if auth_profile.auth_method == ArkAuthMethod.Direct and auth_profile.auth_method_settings:
            direct_method_settings = cast(DirectArkAuthMethodSettings, auth_profile.auth_method_settings)
            if direct_method_settings.endpoint:
                postfix = f'{postfix}_{urlparse(direct_method_settings.endpoint).netloc}'
        return postfix

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

    @abstractmethod
    def _perform_refresh_authentication(self, profile: ArkProfile, auth_profile: ArkAuthProfile, token: ArkToken) -> ArkToken:
        """
        Tries to perform refresh authentication on the existing token
        This is not promised for all authenticators

        Args:
            profile (ArkProfile): _description_
            auth_profile (ArkAuthProfile): _description_
            token (ArkToken): _description_

        Returns:
            ArkToken: _description_
        """

    def authenticate(
        self,
        profile: Optional[ArkProfile] = None,
        auth_profile: Optional[ArkAuthProfile] = None,
        secret: Optional[ArkSecret] = None,
        force: bool = False,
        refresh_auth: bool = False,
    ) -> ArkToken:
        """
        Authenticates with the specified authenticator implementation.
        The implementation is based on the `_perform_authentication` method.
        When caching is allowed, authorization credentials are loaded from the cache.

        Args:
            profile (Optional[ArkProfile]): Profile containing information about the environment and authentication methods
            auth_profile (Optional[ArkAuthProfile]): Specific auth profile to use instead of the profile, when provided
            secret (Optional[ArkSecret]): Secret used for authentication
            force (bool): Determines whether to force authentication without cached credentials
            refresh_auth (bool): Attempts to refresh an existing cached auth when it is available

        Raises:
            ArkAuthException: _description_

        Returns:
            ArkToken: The authentication token to use. The token is also saved in the object.
        """
        if not auth_profile and not profile:
            raise ArkAuthException('Either a profile or a specific auth profile must be supplied')
        if not auth_profile and profile:
            if self.authenticator_name() in profile.auth_profiles:
                auth_profile = profile.auth_profiles[self.authenticator_name()]
            else:
                raise ArkAuthException(
                    f'{self.authenticator_human_readable_name()} [{self.authenticator_name()}] is not defined within the authentication profiles'
                )
        if not profile:
            profile = ArkProfileLoader.load_default_profile()
        if auth_profile.auth_method not in self.supported_auth_methods() and auth_profile.auth_method != ArkAuthMethod.Default:
            raise ArkAuthException(
                f'{self.authenticator_human_readable_name()} does not support authentication method {auth_profile.auth_method.value}'
            )
        if auth_profile.auth_method == ArkAuthMethod.Default:
            auth_profile.auth_method, auth_profile.auth_method_settings = self.default_auth_method()
        if auth_profile.auth_method in ArkAuthMethodsRequireCredentials and not auth_profile.username:
            raise ArkAuthException(f'{self.authenticator_human_readable_name()} requires a username and optionally a secret')
        ark_token = None
        token_refreshed = False
        if self._cache_authentication and self._cache_keyring and not force:
            # Load the postfix of the token based on the auth profile and method type
            ark_token = self._cache_keyring.load_token(profile, self._resolve_cache_postfix(auth_profile))
            if ark_token and ark_token.expires_in.replace(tzinfo=None) <= datetime.now():
                # Expired, try to refresh
                if refresh_auth and ark_token.refresh_token:
                    ark_token = self._perform_refresh_authentication(profile, auth_profile, ark_token)
                    if ark_token:
                        token_refreshed = True
                else:
                    ark_token = None
        if not ark_token:
            ark_token = self._perform_authentication(profile, auth_profile, secret, force)
            if self._cache_authentication and self._cache_keyring:
                self._cache_keyring.save_token(profile, ark_token, self._resolve_cache_postfix(auth_profile))
        elif refresh_auth and not token_refreshed:
            try:
                ark_token = self._perform_refresh_authentication(profile, auth_profile, ark_token)
                if self._cache_authentication and self._cache_keyring:
                    self._cache_keyring.save_token(profile, ark_token, self._resolve_cache_postfix(auth_profile))
            except Exception as ex:  # Fallback to normal authentication
                self._logger.info(
                    f'Refresh auth for [{self.authenticator_human_readable_name()}] failed, falling back to normal authentication [{str(ex)}]'
                )
                ark_token = self._perform_authentication(profile, auth_profile, secret, force)
                if self._cache_authentication and self._cache_keyring:
                    self._cache_keyring.save_token(profile, ark_token, self._resolve_cache_postfix(auth_profile))
        self.__token = ark_token
        self._active_profile = profile
        self._active_auth_profile = auth_profile
        return ark_token

    def is_authenticated(self, profile: ArkProfile) -> bool:
        """
        Checks whether the specified profile is authenticated (has a valid token), either from the keyring or in memory.
        If the valid token originated from the keyring, it is loaded into memory.

        Args:
            profile (ArkProfile): _description_

        Returns:
            bool: _description_
        """
        self._logger.info(f'Checking if [{self.authenticator_name()}] is authenticated')
        if self.__token:
            self._logger.info('Token is already loaded')
            return True
        if self.authenticator_name() in profile.auth_profiles and self._cache_keyring:
            self.__token = self._cache_keyring.load_token(profile, profile.auth_profiles[self.authenticator_name()].username)
            if self.__token and self.__token.expires_in.replace(tzinfo=None) <= datetime.now():
                self.__token = None
            else:
                self._logger.info('Loaded token from cache successfully')
            return self.__token != None
        return False

    def load_authentication(
        self, profile: Optional[ArkProfile] = None, refresh_auth: bool = False, grace_seconds: Optional[int] = None
    ) -> Optional[ArkToken]:
        """
        Loads and returns the authentication token from the cache, if it exists.
        If specified, the method also attempts to refresh the token as needed.

        Args:
            profile (Optional[ArkProfile], optional): _description_. Defaults to None.
            refresh_auth (bool, optional): _description_. Defaults to False.
            grace_seconds (Optional[int], optional): try to refresh in case there is less than grace_seconds until expired. Defaults to None.

        Returns:
            Optional[ArkToken]: _description_
        """
        self._logger.info(f'Trying to load [{self.authenticator_name()}] authentication')
        if not profile:
            if self._active_profile:
                profile = self._active_profile
            else:
                profile = ArkProfileLoader.load_default_profile()
        auth_profile = self._active_auth_profile
        if not auth_profile and self.authenticator_name() in profile.auth_profiles:
            auth_profile = profile.auth_profiles[self.authenticator_name()]
        if auth_profile:
            self._logger.info(
                f'Loading authentication for profile [{profile.profile_name}] and auth profile [{self.authenticator_name()}] of type [{auth_profile.auth_method.value}]'
            )
            if self._cache_keyring:
                self.__token = self._cache_keyring.load_token(profile, self._resolve_cache_postfix(auth_profile))
            if refresh_auth:
                grace_seconds = grace_seconds if grace_seconds is not None else DEFAULT_EXPIRATION_GRACE_DELTA_SECONDS
                if self.__token and self.__token.expires_in.replace(tzinfo=None) - timedelta(seconds=grace_seconds) > datetime.now():
                    self._logger.info('Token did not pass grace expiration, no need to refresh')
                else:
                    self._logger.info('Trying to refresh token authentication')
                    self.__token = self._perform_refresh_authentication(profile, auth_profile, self.__token)
                    if self.__token and self.__token.expires_in.replace(tzinfo=None) > datetime.now():
                        self._logger.info('Token refreshed')
                    if self.__token and self._cache_authentication and self._cache_keyring:
                        self._cache_keyring.save_token(profile, self.__token, self._resolve_cache_postfix(auth_profile))
            if self.__token and self.__token.expires_in.replace(tzinfo=None) <= datetime.now():
                self.__token = None
            if self.__token:
                self._active_profile = profile
                self._active_auth_profile = auth_profile
            return self.__token
        return None

    @property
    def token(self) -> Optional[ArkToken]:
        return self.__token

    @property
    def active_profile(self) -> Optional[ArkProfile]:
        return self._active_profile

    @property
    def active_auth_profile(self) -> Optional[ArkAuthProfile]:
        return self._active_auth_profile

    @staticmethod
    @abstractmethod
    def authenticator_name() -> str:
        """
        Returns the name of the authenticator used for the auth profile and services.

        Returns:
            str: _description_
        """

    @staticmethod
    @abstractmethod
    def authenticator_human_readable_name() -> str:
        """
        Returns the human-readable name of the authenticator.

        Returns:
            str: _description_
        """

    @staticmethod
    @abstractmethod
    def supported_auth_methods() -> List[ArkAuthMethod]:
        """
        Returns the authenticator's supported authentication methods.

        Returns:
            List[ArkAuthMethod]: _description_
        """

    @staticmethod
    @abstractmethod
    def default_auth_method() -> Tuple[ArkAuthMethod, ArkAuthMethodSettings]:
        """
        Returns the default authentication method and settings.

        Returns:
            Tuple[ArkAuthMethod, ArkAuthMethodSettings]: _description_
        """
