import codecs
import json
import logging
import os
import re
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from http import HTTPStatus
from multiprocessing import Pipe, Process, get_context
from multiprocessing.connection import Connection
from typing import Dict, Final, List, Optional, Union

import inquirer
from cachetools import LRUCache, cached
from pydantic import ValidationError
from requests import Session

from ark_sdk_python.args import ArkArgsFormatter, ArkInquirerRender
from ark_sdk_python.auth.identity.ark_identity_fqdn_resolver import ArkIdentityFQDNResolver
from ark_sdk_python.common import ArkKeyring, ArkSystemConfig, get_logger
from ark_sdk_python.common.env import AwsEnv
from ark_sdk_python.models import ArkException, ArkNonInteractiveException
from ark_sdk_python.models.ark_exceptions import ArkAuthException
from ark_sdk_python.models.ark_profile import ArkProfile
from ark_sdk_python.models.auth import ArkAuthMethod, ArkToken, ArkTokenType
from ark_sdk_python.models.common.identity import (
    AdvanceAuthMidResponse,
    AdvanceAuthResponse,
    AdvanceAuthResult,
    Challenge,
    IdpAuthStatusResponse,
    IdpAuthStatusResult,
    Mechanism,
    StartAuthResponse,
    TenantFqdnResponse,
)

RECV_PIPE_INTERVAL: Final[int] = 3.0
POLL_INTERVAL_MS: Final[int] = 0.5
POLL_TIME_SECONDS: Final[int] = 360
SUPPORTED_MECHANISMS: Final[List[str]] = ['pf', 'sms', 'email', 'otp']
MECHANISM_RETRY_COUNT: Final[int] = 20
DEFAULT_TOKEN_LIFETIME_SECONDS: Final[int] = 3600


def input_process(pipe_write: Connection, pipe_read: Connection, mechanism: Mechanism, oob_advance_resp: AdvanceAuthMidResponse) -> None:
    sys.stdin = open(0, encoding='utf-8')
    while True:
        if oob_advance_resp.result.generated_auth_value:
            answers = inquirer.prompt(
                [
                    inquirer.Password(
                        'answer',
                        message=f'Sent Mobile Authenticator request to your device with a value of [{oob_advance_resp.result.generated_auth_value}]. Please follow the instructions to proceed with authentication or enter verification code here.',
                    )
                ],
                render=ArkInquirerRender(),
            )
        else:
            answers = inquirer.prompt([inquirer.Password('answer', message=f'{mechanism.prompt_mech_chosen}')], render=ArkInquirerRender())
        if not answers:
            raise ArkException('Failed to get answer for MFA factor')
        mfa_code = answers['answer']
        pipe_write.send(mfa_code)
        time.sleep(RECV_PIPE_INTERVAL)
        answer = pipe_read.recv()
        if answer == 'CONTINUE':
            continue
        break


class ArkIdentity:
    def __init__(
        self,
        username: str,
        password: Optional[str],
        identity_url: Optional[str] = None,
        identity_tenant_subdomain: Optional[str] = None,
        mfa_type: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        cache_authentication: bool = True,
        verify: Optional[Union[str, bool]] = None,
        load_cache: bool = False,
        cache_profile: Optional[ArkProfile] = None,
    ) -> None:
        self.__username = username
        self.__password = password
        self.__identity_url = self.__resolve_fqdn_from_username_or_subdomain(identity_url, identity_tenant_subdomain)
        if not self.__identity_url.startswith('https://'):
            self.__identity_url = f'https://{self.__identity_url}'
        self.__mfa_type = mfa_type
        self.__logger = logger or get_logger(app=self.__class__.__name__)
        self.__interaction_process: Optional[Process] = None
        self.__is_polling: bool = False
        self.__keyring = ArkKeyring(self.__class__.__name__.lower()) if cache_authentication else None
        self.__cache_authentication = cache_authentication

        self.__session = Session()
        self.__session_details = None
        self.__session_exp = None
        self.__session.headers.update(ArkIdentityFQDNResolver.default_headers())
        if verify is None:
            if ArkSystemConfig.trusted_certificate() is not None:
                verify = ArkSystemConfig.trusted_certificate()
            else:
                verify = ArkSystemConfig.is_verifiying_certificates()
        self.__verify = verify
        self.__session.verify = verify
        if load_cache and cache_authentication and cache_profile:
            self.__load_cache(cache_profile)

    def __load_cache(self, profile: Optional[ArkProfile] = None) -> bool:
        if self.__keyring and profile:
            token = self.__keyring.load_token(profile, f'{self.__username}_identity')
            session = self.__keyring.load_token(profile, f'{self.__username}_identity_session')
            if token and session:
                import dill as pickle

                try:
                    self.__session_details = AdvanceAuthResult.parse_raw(token.token.get_secret_value())
                except ValidationError:
                    self.__session_details = IdpAuthStatusResult.parse_raw(token.token.get_secret_value())
                self.__session_exp = token.expires_in
                self.__session = pickle.loads(codecs.decode(session.token.get_secret_value().encode(), "base64"))
                self.__session.verify = self.__verify
                self.__identity_url = token.endpoint
                return True
        return False

    def __save_cache(self, profile: Optional[ArkProfile] = None) -> None:
        if self.__keyring and profile and self.__session_details:
            import dill as pickle

            delta = self.__session_details.token_lifetime or DEFAULT_TOKEN_LIFETIME_SECONDS
            self.__session_exp = datetime.now() + timedelta(seconds=delta)
            self.__keyring.save_token(
                profile,
                ArkToken(
                    token=self.__session_details.json(),
                    username=self.__username,
                    endpoint=self.__identity_url,
                    token_type=ArkTokenType.Internal,
                    auth_method=ArkAuthMethod.Other,
                    expires_in=self.__session_exp,
                    refresh_token=self.__session_details.refresh_token,
                ),
                f'{self.__username}_identity',
            )
            self.__keyring.save_token(
                profile,
                ArkToken(
                    token=codecs.encode(pickle.dumps(self.__session), 'base64').decode(),
                    username=self.__username,
                    endpoint=self.__identity_url,
                    token_type=ArkTokenType.Internal,
                    auth_method=ArkAuthMethod.Other,
                    expires_in=self.__session_exp,
                ),
                f'{self.__username}_identity_session',
            )

    def __resolve_fqdn_from_username_or_subdomain(self, identity_url: Optional[str], identity_tenant_subdomain: Optional[str]) -> str:
        if identity_tenant_subdomain and not identity_url:
            try:
                identity_url = ArkIdentityFQDNResolver.resolve_tenant_fqdn_from_tenant_subdomain(
                    identity_tenant_subdomain, AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
                )
            except Exception as ex:
                self.__logger.warning(f'Failed to resolve url from tenant subdomain, falling back to user [{str(ex)}]')
        if identity_url:
            return identity_url
        tenant_suffix = self.__username[self.__username.index('@') :]
        return ArkIdentityFQDNResolver.resolve_tenant_fqdn_from_tenant_suffix(tenant_suffix=tenant_suffix)

    def __start_authentication(self) -> StartAuthResponse:
        self.__logger.info(f'Starting authentication with user {self.__username} and fqdn {self.__identity_url}')
        response = self.__session.post(
            url=f'{self.__identity_url}/Security/StartAuthentication',
            json={'User': self.__username, 'Version': '1.0', 'PlatformTokenResponse': True, 'MfaRequestor': 'DeviceAgent'},
        )
        try:
            parsed_res: StartAuthResponse = StartAuthResponse.parse_raw(response.text)
            if not parsed_res.result.challenges and not parsed_res.result.idp_redirect_url:
                raise ValidationError('No challenges or idp redirect url on start auth')
        except (ValidationError, TypeError) as ex:
            try:
                if 'PodFqdn' in response.text:
                    fqdn = TenantFqdnResponse.parse_raw(response.text)
                    self.__identity_url = f'https://{fqdn.result.pod_fqdn}'
                    self.__session = Session()
                    self.__session.verify = self.__verify
                    self.__session.headers.update(ArkIdentityFQDNResolver.default_headers())
                    return self.__start_authentication()
            except Exception:
                pass
            raise ArkException('Identity start authentication failed to be parsed / validated') from ex
        return parsed_res

    def __advance_authentication(
        self, mechanism_id: str, session_id: str, answer: str, action: str
    ) -> Union[AdvanceAuthMidResponse, AdvanceAuthResponse]:
        self.__logger.info(f'Advancing authentication with user {self.__username} and fqdn {self.__identity_url} and action {action}')
        response = self.__session.post(
            url=f'{self.__identity_url}/Security/AdvanceAuthentication',
            json={'SessionId': session_id, 'MechanismId': mechanism_id, 'Action': action, 'Answer': answer},
        )
        try:
            parsed_res: AdvanceAuthMidResponse = AdvanceAuthMidResponse.parse_raw(response.text)
            if parsed_res.result.summary == 'LoginSuccess':
                parsed_res: AdvanceAuthResponse = AdvanceAuthResponse.parse_raw(response.text)
        except (ValidationError, TypeError) as ex:
            raise ArkException(f'Identity advance authentication failed to be parsed / validated [{response.text}]') from ex
        return parsed_res

    def __identity_idp_auth_status(self, session_id: str) -> IdpAuthStatusResponse:
        self.__logger.info(f'Calling idp auth status for fqdn {self.__identity_url} and session id {session_id}')
        response = self.__session.post(
            url=f'{self.__identity_url}/Security/OobAuthStatus',
            json={'SessionId': session_id},
        )
        try:
            parsed_res: IdpAuthStatusResponse = IdpAuthStatusResponse.parse_raw(response.text)
        except (ValidationError, TypeError) as ex:
            raise ArkException(f'Identity idp auth status failed to be parsed / validated [{response.text}]') from ex
        return parsed_res

    def __start_input_process(
        self, pipe_write: Connection, pipe_read: Connection, mechanism: Mechanism, oob_advance_resp: AdvanceAuthMidResponse
    ) -> None:
        if self.__interaction_process:
            raise ArkException('Interaction thread is already in progress')
        if sys.platform not in ['win32', 'cygwin']:
            ctx = get_context('fork')
        else:
            ctx = get_context('spawn')
        self.__interaction_process = ctx.Process(
            target=input_process,
            args=(
                pipe_write,
                pipe_read,
                mechanism,
                oob_advance_resp,
            ),
        )
        self.__interaction_process.start()

    def __stop_input_process(self) -> None:
        if self.__interaction_process:
            self.__interaction_process.kill()
            self.__interaction_process.join()
            self.__interaction_process = None

    def __poll_authentication(
        self,
        profile: ArkProfile,
        mechanism: Mechanism,
        start_auth_response: StartAuthResponse,
        oob_advance_resp: AdvanceAuthMidResponse,
        is_interactive: bool,
    ) -> None:
        try:
            if self.__is_polling:
                raise ArkException('MFA Polling is already in progress')
            self.__is_polling = True
            input_conn, output_conn = Pipe(duplex=True)
            if is_interactive:
                self.__start_input_process(input_conn, output_conn, mechanism, oob_advance_resp)
            start_time = datetime.now()
            while self.__is_polling:
                current_time = datetime.now()
                if (current_time - start_time).seconds >= POLL_TIME_SECONDS:
                    self.__is_polling = False
                    raise ArkException('Timeout reached while polling for user answer')
                if output_conn.poll():
                    mfa_code = output_conn.recv()
                    advance_resp = self.__advance_authentication(
                        mechanism.mechanism_id, start_auth_response.result.session_id, mfa_code, 'Answer'
                    )
                    if isinstance(advance_resp, AdvanceAuthResponse):
                        input_conn.send('DONE')
                    else:
                        input_conn.send('CONTINUE')
                else:
                    advance_resp = self.__advance_authentication(mechanism.mechanism_id, start_auth_response.result.session_id, '', 'Poll')
                if isinstance(advance_resp, AdvanceAuthResponse):
                    # Done here, save the token
                    self.__is_polling = False
                    if is_interactive:
                        self.__stop_input_process()
                    self.__session_details = advance_resp.result
                    self.__session.headers.update(
                        {'Authorization': f'Bearer {advance_resp.result.auth}', **ArkIdentityFQDNResolver.default_headers()}
                    )
                    delta = self.__session_details.token_lifetime or DEFAULT_TOKEN_LIFETIME_SECONDS
                    self.__session_exp = datetime.now() + timedelta(seconds=delta)
                    if self.__cache_authentication:
                        self.__save_cache(profile)
                    return
                time.sleep(POLL_INTERVAL_MS)
        except Exception as ex:
            if is_interactive:
                self.__stop_input_process()
            if not self.__session_details:
                raise ex
        finally:
            if is_interactive:
                self.__stop_input_process()

    def __pick_mechanism(self, challenge: Challenge) -> Mechanism:
        factors = {'otp': '📲 Push / Code', 'sms': '📟 SMS', 'email': '📧 Email', 'pf': '📞 Phone call'}
        supported_mechanisms = [m for m in challenge.mechanisms if m.name.lower() in SUPPORTED_MECHANISMS]
        answers = inquirer.prompt(
            [
                inquirer.List(
                    'mfa',
                    'Please pick one of the following MFA methods',
                    choices=[factors[m.name.lower()] for m in supported_mechanisms],
                    default=factors[self.__mfa_type] if self.__mfa_type and self.__mfa_type in factors else None,
                    carousel=True,
                )
            ],
            render=ArkInquirerRender(),
        )
        if not answers:
            raise ArkException('Failed to get answer for which MFA method to use')
        self.__mfa_type = next(filter(lambda f: factors[f] == answers['mfa'], factors.keys()))
        return next(filter(lambda m: factors[m.name.lower()] == answers['mfa'], supported_mechanisms))

    def __perform_idp_authentication(
        self, start_auth_response: StartAuthResponse, profile: Optional[ArkProfile] = None, interactive: bool = False
    ) -> None:
        if self.__is_polling:
            raise ArkException('MFA / IDP Polling is already in progress')
        # Print the user some info if we are interactive
        if interactive:
            ArkArgsFormatter.print_normal_bright(
                "\nYou are now being redirected from your browser to your external identity provider for authentication\n"
                "If the browser did not open, you may also click the following URL to access your identity provider authentication\n\n"
                f"{start_auth_response.result.idp_redirect_short_url}\n"
            )

        # Error can be ignored
        webbrowser.open(start_auth_response.result.idp_redirect_short_url, new=0, autoraise=True)

        # Start polling for idp auth
        self.__is_polling = True
        start_time = datetime.now()
        while self.__is_polling:
            current_time = datetime.now()
            if (current_time - start_time).seconds >= POLL_TIME_SECONDS:
                self.__is_polling = False
                raise ArkException('Timeout reached while polling for idp auth')
            idp_auth_status = self.__identity_idp_auth_status(start_auth_response.result.idp_login_session_id)
            if idp_auth_status.result.state == 'Success' and idp_auth_status.result.token:
                # We managed to successfully authenticate
                # Done here, save the token
                self.__session_details = idp_auth_status.result
                self.__session.headers.update(
                    {'Authorization': f'Bearer {idp_auth_status.result.token}', **ArkIdentityFQDNResolver.default_headers()}
                )
                delta = self.__session_details.token_lifetime or DEFAULT_TOKEN_LIFETIME_SECONDS
                self.__session_exp = datetime.now() + timedelta(seconds=delta)
                if self.__cache_authentication:
                    self.__save_cache(profile)
                break
            time.sleep(POLL_INTERVAL_MS)

    @classmethod
    def has_cache_record(cls, profile: ArkProfile, username: str, refresh_auth_allowed: bool) -> bool:
        """
        Checks if a cache record exists for the specified profile and username.

        Args:
            profile (ArkProfile): _description_
            username (str): _description_
            refresh_auth_allowed (bool): _description_

        Returns:
            bool: _description_
        """
        keyring = ArkKeyring(cls.__name__.lower())
        token = keyring.load_token(profile, f'{username}_identity')
        session = keyring.load_token(profile, f'{username}_identity_session')
        if token is not None and session is not None:
            if token.expires_in and token.expires_in < datetime.now():
                if token.refresh_token and refresh_auth_allowed:
                    return True
                return False
            return True
        return False

    @classmethod
    @cached(cache=LRUCache(maxsize=1024))
    def is_idp_user(cls, username: str, identity_url: Optional[str], identity_tenant_subdomain: Optional[str]) -> bool:
        """
        Checks whether or not the specified username is from an external IDP.

        Args:
            username (str): _description_
            identity_url (Optional[str]): _description_
            identity_tenant_subdomain (Optional[str]): _description_

        Returns:
            bool: _description_
        """
        if re.match('.*@cyberark\\.cloud\\.(\\d)+', username) is not None:
            return False
        identity = ArkIdentity(
            username=username,
            password='',
            identity_url=identity_url,
            identity_tenant_subdomain=identity_tenant_subdomain,
        )
        resp = identity.__start_authentication()
        return resp.result.idp_redirect_url != None

    def get_apps(self) -> Dict:
        """
        Returns the applications to which the user is logged in.

        Raises:
            ArkException: _description_

        Returns:
            Dict: _description_
        """
        if not self.__session_details:
            raise ArkException('Identity authentication is required first')
        cookies = self.__session.cookies.copy()
        response = self.__session.post(url=f'{self.__identity_url}/UPRest/GetUPData')
        self.__session.cookies = cookies
        return json.loads(response.text)

    def auth_identity(self, profile: Optional[ArkProfile] = None, interactive: bool = False, force: bool = False) -> None:
        """
        Authenticates to Identity with the information specified in the constructor.
        If MFA is configured and `interactive` is enabled, the user is prompted for the MFA secret.
        The auth token and other details are stored in the object for future use.

        Args:
            profile (Optional[ArkProfile]): Profile to use (loaded from cache, if available)
            interactive (bool): Determines whether interactive user prompts are allowed
            force (bool): Determines whether to ignore cache and force authentication (defaults to false)

        Raises:
            ArkException: _description_
        """
        self.__logger.debug('Attempting to authenticate to Identity')
        self.__session_details = None
        if self.__cache_authentication and not force and self.__load_cache(profile):
            # Check if expired
            if self.__session_exp.replace(tzinfo=None) > datetime.now():
                self.__logger.info('Loaded identity details from cache')
                return
        self.__session = Session()
        self.__session.verify = self.__verify
        self.__session.headers.update(ArkIdentityFQDNResolver.default_headers())

        # Start the authentication
        start_auth_response = self.__start_authentication()
        if start_auth_response.result.idp_redirect_url:
            # External IDP Flow, ignore the mechanisms and just open a browser
            self.__perform_idp_authentication(start_auth_response, profile, interactive)
            return

        # Check if password is part of the first challenges list and if so, answer it directly
        current_challenge_idx = 0
        for mechanism in start_auth_response.result.challenges[current_challenge_idx].mechanisms:
            if mechanism.name.lower() == 'up':
                current_challenge_idx += 1
                # Password, answer it
                if not self.__password:
                    if not interactive:
                        raise ArkAuthException('No password and not interactive, cannot continue')
                    answers = inquirer.prompt(
                        [inquirer.Password('answer', message='Identity Security Platform Secret')],
                        render=ArkInquirerRender(),
                    )
                    if not answers:
                        raise ArkAuthException('Canceled by user')
                    self.__password = answers['answer']
                advance_resp = self.__advance_authentication(
                    mechanism.mechanism_id, start_auth_response.result.session_id, self.__password, 'Answer'
                )
                if isinstance(advance_resp, AdvanceAuthResponse) and len(start_auth_response.result.challenges) == 1:
                    # Done here, save the token
                    self.__session_details = advance_resp.result
                    self.__session.headers.update(
                        {'Authorization': f'Bearer {advance_resp.result.auth}', **ArkIdentityFQDNResolver.default_headers()}
                    )
                    delta = self.__session_details.token_lifetime or DEFAULT_TOKEN_LIFETIME_SECONDS
                    self.__session_exp = datetime.now() + timedelta(seconds=delta)
                    if self.__cache_authentication:
                        self.__save_cache(profile)
                    return
                break

        # Pick MFA for the user
        if interactive:
            self.__pick_mechanism(start_auth_response.result.challenges[current_challenge_idx])

        # Handle a case where MFA type was supplied
        if self.__mfa_type and self.__mfa_type.lower() in SUPPORTED_MECHANISMS and current_challenge_idx == 1:
            for mechanism in start_auth_response.result.challenges[current_challenge_idx].mechanisms:
                if mechanism.name.lower() == self.__mfa_type.lower():
                    oob_advance_resp = self.__advance_authentication(
                        mechanism.mechanism_id, start_auth_response.result.session_id, '', 'StartOOB'
                    )
                    self.__poll_authentication(profile, mechanism, start_auth_response, oob_advance_resp, interactive)
                    return

        if not interactive:
            raise ArkNonInteractiveException('User interaction is not supported while not interactive and mfa type given was not found')

        # Handle the rest of the challenges, might also handle the first challenge if no password is in the mechanisms
        for challenge in start_auth_response.result.challenges[current_challenge_idx:]:
            mechanism = self.__pick_mechanism(challenge)
            oob_advance_resp = self.__advance_authentication(mechanism.mechanism_id, start_auth_response.result.session_id, '', 'StartOOB')
            self.__poll_authentication(profile, mechanism, start_auth_response, oob_advance_resp, interactive)

    # pylint: disable=unused-argument
    def refresh_auth_identity(self, profile: Optional[ArkProfile] = None, interactive: bool = False, force: bool = False) -> None:
        """
        Performs a token refresh with the object's existing details.

        Args:
            profile (Optional[ArkProfile]): The profile to load from the cache, if available
            force (bool): Determines whether to ignore cache and force authentication (defaults to false)

        Raises:
            ArkAuthException: _description_
        """
        from jose.jwt import get_unverified_claims

        if not self.__session_details.token:
            # We only refresh platform token at the moment, call the normal authentication instead
            return self.auth_identity(profile, interactive, force)

        self.__logger.debug('Attempting to refresh authenticate to Identity')
        self.__session = Session()
        self.__session.verify = self.__verify
        self.__session.headers.update(ArkIdentityFQDNResolver.default_headers())
        decoded_token = get_unverified_claims(self.__session_details.token)
        platform_tenant_id = decoded_token['tenant_id']
        cookies = {
            f'refreshToken-{platform_tenant_id}': self.__session_details.refresh_token,
            f'idToken-{platform_tenant_id}': self.__session_details.token,
        }
        response = self.__session.post(
            url=f'{self.__identity_url}/OAuth2/RefreshPlatformToken',
            cookies=cookies,
        )
        if response.status_code != HTTPStatus.OK:
            raise ArkAuthException('Failed to refresh token')
        new_token = response.cookies.get(f'idToken-{platform_tenant_id}')
        new_refresh_token = response.cookies.get(f'refreshToken-{platform_tenant_id}')
        if not new_token or not new_refresh_token:
            raise ArkAuthException('Failed to retrieve refresh tokens cookies')
        self.__session_details.token = new_token
        self.__session_details.refresh_token = new_refresh_token
        self.__session_details.token_lifetime = (
            datetime.fromtimestamp(get_unverified_claims(new_token)['exp'])
            - datetime.fromtimestamp(get_unverified_claims(new_token)['iat'])
        ).seconds
        delta = self.__session_details.token_lifetime or DEFAULT_TOKEN_LIFETIME_SECONDS
        self.__session_exp = datetime.now() + timedelta(seconds=delta)
        if self.__cache_authentication:
            self.__save_cache(profile)

    @property
    def session(self) -> Session:
        return self.__session

    @property
    def session_token(self) -> Optional[str]:
        if self.__session_details:
            if self.__session_details.token:
                return self.__session_details.token
            if 'auth' in self.__session_details.__dict__ and self.__session_details.auth:
                return self.__session_details.auth
        return None

    @property
    def session_details(self) -> Optional[AdvanceAuthResult]:
        return self.__session_details

    @property
    def identity_url(self) -> str:
        return self.__identity_url
