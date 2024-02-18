# pylint: disable=unused-argument
import codecs
import os
import pickle
from datetime import datetime, timedelta
from typing import Final, List, Optional, Tuple, cast

from overrides import overrides

from ark_sdk_python.auth.ark_auth import ArkAuth
from ark_sdk_python.auth.identity.ark_identity import ArkIdentity
from ark_sdk_python.auth.identity.ark_identity_service_user import ArkIdentityServiceUser
from ark_sdk_python.common.ark_system_config import ArkSystemConfig
from ark_sdk_python.common.env import ROOT_DOMAIN, AwsEnv
from ark_sdk_python.models import ArkProfile
from ark_sdk_python.models.ark_exceptions import ArkAuthException, ArkException
from ark_sdk_python.models.auth import (
    ArkAuthMethod,
    ArkAuthMethodSettings,
    ArkAuthProfile,
    ArkSecret,
    ArkToken,
    ArkTokenType,
    IdentityArkAuthMethodSettings,
    IdentityServiceUserArkAuthMethodSettings,
)

AUTH_NAME: Final[str] = 'isp'
AUTH_HUMAN_READABLE_NAME: Final[str] = 'Identity Security Platform'
AUTH_METHODS: Final[List[ArkAuthMethod]] = [
    ArkAuthMethod.Identity,
    ArkAuthMethod.IdentityServiceUser,
]
DEFAULT_AUTH_METHOD: Final[ArkAuthMethod] = ArkAuthMethod.Identity
DEFAULT_AUTH_METHOD_SETTINGS: Final[IdentityArkAuthMethodSettings] = IdentityArkAuthMethodSettings()
DEFAULT_TOKEN_LIFETIME: Final[int] = 3600


class ArkISPAuth(ArkAuth):
    def __perform_identity_authentication(
        self, profile: ArkProfile, auth_profile: ArkAuthProfile, secret: Optional[ArkSecret], force: bool
    ) -> ArkToken:
        try:
            method_settings = cast(IdentityArkAuthMethodSettings, auth_profile.auth_method_settings)
            identity = ArkIdentity(
                username=auth_profile.username,
                password=secret.secret.get_secret_value() if secret else None,
                identity_url=method_settings.identity_url,
                identity_tenant_subdomain=method_settings.identity_tenant_subdomain,
                mfa_type=method_settings.identity_mfa_method,
                logger=self._logger,
                cache_authentication=self._cache_authentication,
            )
            identity.auth_identity(profile, ArkSystemConfig.is_interactive() and method_settings.identity_mfa_interactive, force)
            env = AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
            found_env = list(filter(lambda e: ROOT_DOMAIN[e] in identity.identity_url, ROOT_DOMAIN.keys()))
            if found_env:
                env = found_env[0]
            token_lifetime = identity.session_details.token_lifetime
            if not token_lifetime:
                token_lifetime = DEFAULT_TOKEN_LIFETIME
            return ArkToken(
                token=identity.session_token,
                username=auth_profile.username,
                endpoint=identity.identity_url,
                token_type=ArkTokenType.JWT,
                auth_method=ArkAuthMethod.Identity,
                expires_in=datetime.now() + timedelta(seconds=token_lifetime),
                refresh_token=identity.session_details.refresh_token,
                metadata={'env': env, 'cookies': codecs.encode(pickle.dumps(identity.session.cookies), 'base64').decode()},
            )
        except Exception as ex:
            self._logger.exception(f'Failed to authenticate to identity security platform [{str(ex)}]')
            raise ArkAuthException from ex

    def __perform_identity_refresh_authentication(self, profile: ArkProfile, auth_profile: ArkAuthProfile, token: ArkToken) -> ArkToken:
        try:
            method_settings = cast(IdentityArkAuthMethodSettings, auth_profile.auth_method_settings)
            identity = ArkIdentity(
                username=auth_profile.username,
                password=None,
                identity_url=method_settings.identity_url,
                mfa_type=method_settings.identity_mfa_method,
                logger=self._logger,
                cache_authentication=self._cache_authentication,
                load_cache=True,
                cache_profile=profile,
            )
            identity.refresh_auth_identity(profile, method_settings.identity_mfa_interactive, False)
            env = AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
            found_env = list(filter(lambda e: ROOT_DOMAIN[e] in identity.identity_url, ROOT_DOMAIN.keys()))
            if found_env:
                env = found_env[0]
            token_lifetime = identity.session_details.token_lifetime
            if not token_lifetime:
                token_lifetime = DEFAULT_TOKEN_LIFETIME
            return ArkToken(
                token=identity.session_token,
                username=auth_profile.username,
                endpoint=identity.identity_url,
                token_type=ArkTokenType.JWT,
                auth_method=ArkAuthMethod.Identity,
                expires_in=datetime.now() + timedelta(seconds=token_lifetime),
                refresh_token=identity.session_details.refresh_token,
                metadata={'env': env, 'cookies': codecs.encode(pickle.dumps(identity.session.cookies), 'base64').decode()},
            )
        except Exception as ex:
            raise ArkAuthException('Failed to authenticate to isp via identity') from ex

    def __perform_identity_service_user_authentication(
        self, profile: ArkProfile, auth_profile: ArkAuthProfile, secret: Optional[ArkSecret], force: bool
    ) -> ArkToken:
        try:
            if not secret:
                raise ArkException('Token secret is required for identity service user auth')
            method_settings = cast(IdentityServiceUserArkAuthMethodSettings, auth_profile.auth_method_settings)
            identity = ArkIdentityServiceUser(
                username=auth_profile.username,
                token=secret.secret.get_secret_value(),
                app_name=method_settings.identity_authorization_application,
                logger=self._logger,
                cache_authentication=self._cache_authentication,
            )
            identity.auth_identity(profile, force)
            env = AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
            found_env = list(filter(lambda e: ROOT_DOMAIN[e] in identity.identity_url, ROOT_DOMAIN.keys()))
            if found_env:
                env = found_env[0]
            return ArkToken(
                token=identity.session_token,
                username=auth_profile.username,
                endpoint=identity.identity_url,
                token_type=ArkTokenType.JWT,
                auth_method=ArkAuthMethod.IdentityServiceUser,
                expires_in=datetime.now() + timedelta(hours=4),
                metadata={'env': env, 'cookies': codecs.encode(pickle.dumps(identity.session.cookies), 'base64').decode()},
            )
        except Exception as ex:
            self._logger.exception(f'Failed to authenticate to identity security platform with service user [{str(ex)}]')
            raise ArkAuthException from ex

    @overrides
    def _perform_authentication(
        self, profile: ArkProfile, auth_profile: ArkAuthProfile, secret: Optional[ArkSecret] = None, force: bool = False
    ) -> ArkToken:
        """
        Performs authentication to the identity security platform identity tenant
        Authentication can be done with either a service user or a normal user
        Authentication Methods:
        - Identity, Default
        - IdentityServiceUser

        Args:
            profile (ArkProfile): _description_
            auth_profile (ArkAuthProfile): _description_
            secret (Optional[ArkSecret], optional): _description_. Defaults to None.
            force (bool, optional): _description_. Defaults to False.

        Raises:
            ArkAuthException: _description_

        Returns:
            ArkToken: _description_
        """
        self._logger.info('Performing authentication to ISP')
        if auth_profile.auth_method in [ArkAuthMethod.Identity, ArkAuthMethod.Default]:
            return self.__perform_identity_authentication(profile, auth_profile, secret, force)
        if auth_profile.auth_method == ArkAuthMethod.IdentityServiceUser:
            return self.__perform_identity_service_user_authentication(profile, auth_profile, secret, force)
        raise ArkAuthException('Given auth method is not supported')

    @overrides
    def _perform_refresh_authentication(self, profile: ArkProfile, auth_profile: ArkAuthProfile, token: ArkToken) -> ArkToken:
        """
        Refresh for isp tenant is supported only for identity

        Args:
            profile (ArkProfile): _description_
            auth_profile (ArkAuthProfile): _description_
            token (ArkToken): _description_

        Returns:
            ArkToken: _description_
        """
        self._logger.info('Performing refresh authentication to ISP')
        if auth_profile.auth_method in [ArkAuthMethod.Identity, ArkAuthMethod.Default]:
            return self.__perform_identity_refresh_authentication(profile, auth_profile, token)
        return token

    @staticmethod
    @overrides
    def authenticator_name() -> str:
        return AUTH_NAME

    @staticmethod
    @overrides
    def authenticator_human_readable_name() -> str:
        return AUTH_HUMAN_READABLE_NAME

    @staticmethod
    @overrides
    def supported_auth_methods() -> List[ArkAuthMethod]:
        return AUTH_METHODS

    @staticmethod
    @overrides
    def default_auth_method() -> Tuple[ArkAuthMethod, ArkAuthMethodSettings]:
        return DEFAULT_AUTH_METHOD, DEFAULT_AUTH_METHOD_SETTINGS
