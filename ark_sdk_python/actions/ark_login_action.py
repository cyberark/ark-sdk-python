import argparse
from typing import Dict, List, Tuple

from overrides import overrides

from ark_sdk_python.actions.ark_action import ArkAction
from ark_sdk_python.args import ArkArgsFormatter
from ark_sdk_python.auth import SUPPORTED_AUTHENTICATORS, SUPPORTED_AUTHENTICATORS_LIST
from ark_sdk_python.auth.identity import ArkIdentity
from ark_sdk_python.common import ArkSystemConfig
from ark_sdk_python.models import ArkException
from ark_sdk_python.models.ark_profile import ArkProfileLoader
from ark_sdk_python.models.auth import (
    ArkAuthMethod,
    ArkAuthMethodSharableCredentials,
    ArkAuthMethodsRequireCredentials,
    ArkSecret,
    ArkToken,
    IdentityArkAuthMethodSettings,
)


class ArkLoginAction(ArkAction):
    @overrides
    def define_action(self, subparsers: argparse._SubParsersAction) -> None:
        """
        Defines the CLI `login` action.
        For each supported authenticator, adds the username/secret params for logging in.

        Args:
            subparsers (argparse._SubParsersAction): _description_
        """
        login_parser: argparse.ArgumentParser = subparsers.add_parser('login')
        self._common_actions_configuration(login_parser)
        login_parser.add_argument('-pn', '--profile-name', default=ArkProfileLoader.default_profile_name(), help='Profile name to load')
        login_parser.add_argument('-f', '--force', action='store_true', help='Whether to force login even thou token has not expired yet')
        login_parser.add_argument(
            '-nss',
            '--no-shared-secrets',
            action='store_true',
            help='Do not share secrets between different authenticators with the same username',
        )
        login_parser.add_argument('-st', '--show-tokens', action='store_true', help='Print out tokens as well if not silent')
        login_parser.add_argument('-ra', '--refresh-auth', action='store_true', help='If a cache exists, will also try to refresh it')

        # Add username and secret for each authenticator for logging in
        for authenticator in SUPPORTED_AUTHENTICATORS_LIST:
            login_parser.add_argument(
                f'-{"".join([s[:2] for s in authenticator.authenticator_name().split("_")])}u',
                f'--{authenticator.authenticator_name().replace("_", "-")}-username',
                help=f'Username to authenticate with to {authenticator.authenticator_human_readable_name()}',
            )
            login_parser.add_argument(
                f'-{"".join([s[:2] for s in authenticator.authenticator_name().split("_")])}s',
                f'--{authenticator.authenticator_name().replace("_", "-")}-secret',
                help=f'Secret to authenticate with to {authenticator.authenticator_human_readable_name()}',
            )

    @overrides
    def run_action(self, args: argparse.Namespace) -> None:
        """
        Runs the login action for each authenticator.
        After a login completes, credentials are stored in the keyring for future use.

        Args:
            args (argparse.Namespace): _description_

        Raises:
            ArkException: _description_
            ArkException: _description_
        """
        self._common_actions_execution(args)
        # Load up the profile
        profile = ArkProfileLoader.load_profile(ArkProfileLoader.deduce_profile_name(args.profile_name))
        if not profile:
            raise ArkException('Please configure a profile before trying to login')

        # Login for each auth profile
        # Share secrets between authenticators for allowed auth methods
        shared_secrets_map: Dict[ArkAuthMethod, List[Tuple[str, ArkSecret]]] = {k: [] for k in ArkAuthMethodSharableCredentials}
        # Save tokens for finalization output
        tokens_map: Dict[str, ArkToken] = dict()
        for authenticator_name, auth_profile in profile.auth_profiles.items():
            authenticator = SUPPORTED_AUTHENTICATORS[authenticator_name]()

            # Only perform the authentication if not already authenticated and not forced
            if authenticator.is_authenticated(profile) and not args.force:
                try:
                    if args.refresh_auth:
                        token = authenticator.load_authentication(profile, True)
                        if token:
                            ArkArgsFormatter.print_success(
                                f'{authenticator.authenticator_human_readable_name()} Authentication Refreshed',
                            )
                        else:
                            raise ArkException(f'{authenticator.authenticator_name()} authentication failed to be refreshed')
                    else:
                        ArkArgsFormatter.print_success(
                            f'{authenticator.authenticator_human_readable_name()} Already Authenticated',
                        )
                    continue
                except Exception as ex:
                    self._logger.info(
                        f'{authenticator.authenticator_human_readable_name()} Failed to refresh token, performing normal login [{str(ex)}]'
                    )
            secret = (
                ArkSecret(secret=args.__dict__[f'{authenticator_name}_secret']) if args.__dict__[f'{authenticator_name}_secret'] else None
            )
            auth_profile.username = args.__dict__[f'{authenticator_name}_username'] or auth_profile.username

            # Ask the user for the user and secret if interactive
            if ArkSystemConfig.is_interactive() and auth_profile.auth_method in ArkAuthMethodsRequireCredentials:
                auth_profile.username = ArkArgsFormatter.get_arg(
                    args,
                    f'{authenticator_name}_username',
                    f'{authenticator.authenticator_human_readable_name()} Username',
                    auth_profile.username,
                )
                # Check if there is an existing secret who is sharable
                if (
                    auth_profile.auth_method in ArkAuthMethodSharableCredentials
                    and auth_profile.auth_method in shared_secrets_map
                    and any(auth_profile.username == s[0] for s in shared_secrets_map[auth_profile.auth_method])
                    and not args.__dict__[f'{authenticator_name}_secret']
                    and not args.no_shared_secrets
                ):
                    secret = next(filter(lambda s: auth_profile.username == s[0], shared_secrets_map[auth_profile.auth_method]))[1]
                else:
                    if not args.force and (
                        (
                            auth_profile.auth_method == ArkAuthMethod.Identity
                            and ArkIdentity.has_cache_record(profile, auth_profile.username, args.refresh_auth)
                        )
                    ):
                        # Check if there is a secret already cached, if there is, no need to ask for password
                        secret = ArkSecret(secret='')
                    else:
                        # Check if we really need to ask for a password in specific use cases
                        if (
                            authenticator_name == 'isp'
                            and auth_profile.auth_method == ArkAuthMethod.Identity
                            and ArkIdentity.is_idp_user(
                                auth_profile.username,
                                (
                                    auth_profile.auth_method_settings.identity_url
                                    if isinstance(auth_profile.auth_method_settings, IdentityArkAuthMethodSettings)
                                    else None
                                ),
                                (
                                    auth_profile.auth_method_settings.identity_tenant_subdomain
                                    if isinstance(auth_profile.auth_method_settings, IdentityArkAuthMethodSettings)
                                    else None
                                ),
                            )
                        ):
                            secret = ArkSecret(secret='')
                        else:
                            secret = ArkSecret(
                                secret=ArkArgsFormatter.get_arg(
                                    args,
                                    f'{authenticator_name}_secret',
                                    f'{authenticator.authenticator_human_readable_name()} Secret',
                                    hidden=True,
                                )
                            )
            elif (
                not ArkSystemConfig.is_interactive()
                and auth_profile.auth_method in ArkAuthMethodsRequireCredentials
                and not args.__dict__[f'{authenticator_name}_secret']
            ):
                raise ArkException(
                    f'{authenticator_name}-secret argument is required if authenticating to {authenticator.authenticator_human_readable_name()}'
                )
            # Perform the authentication, will also cache the token
            token = authenticator.authenticate(profile=profile, secret=secret, force=args.force, refresh_auth=args.refresh_auth)
            if not args.no_shared_secrets and auth_profile.auth_method in ArkAuthMethodSharableCredentials:
                shared_secrets_map[auth_profile.auth_method].append((auth_profile.username, secret))
            tokens_map[authenticator.authenticator_human_readable_name()] = token
        if not args.show_tokens and tokens_map:
            ArkArgsFormatter.print_success('Login tokens are hidden')
        for k, v in tokens_map.items():
            if 'cookies' in v.metadata:
                del v.metadata['cookies']
            ArkArgsFormatter.print_success(
                f'{k} Token\n{v.json(indent=4, exclude={} if args.show_tokens else {"token", "refresh_token"})}',
            )

    @overrides
    def can_run_action(self, action_name: str, args: argparse.Namespace) -> bool:
        """
        Asserts the action is `login`.

        Args:
            action_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
        return action_name == 'login'
