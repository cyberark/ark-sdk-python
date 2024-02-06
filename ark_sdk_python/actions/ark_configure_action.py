import argparse
from typing import Optional

from overrides import overrides

from ark_sdk_python.actions.ark_action import ArkAction
from ark_sdk_python.args import ArkArgsFormatter, ArkPydanticArgparse
from ark_sdk_python.auth import SUPPORTED_AUTHENTICATORS_LIST
from ark_sdk_python.common import ArkSystemConfig
from ark_sdk_python.models import ArkException, ArkProfile, ArkProfileLoader
from ark_sdk_python.models.actions import (
    CONFIGURATION_ALLOWED_EMPTY_VALUES,
    CONFIGURATION_AUTHENTICATOR_IGNORED_DEFNITION_KEYS,
    CONFIGURATION_AUTHENTICATOR_IGNORED_INTERACTIVE_KEYS,
    CONFIGURATION_AUTHENTICATORS_DEFAULTS,
    CONFIGURATION_IGNORED_DEFINITION_KEYS,
    CONFIGURATION_IGNORED_INTERACTIVE_KEYS,
    CONFIGURATION_OVERRIDE_ALIASES,
)
from ark_sdk_python.models.auth import (
    ArkAuthMethod,
    ArkAuthMethodsDescriptionMap,
    ArkAuthMethodSettingsMap,
    ArkAuthMethodsRequireCredentials,
    ArkAuthProfile,
)


class ArkConfigureAction(ArkAction):
    @overrides
    def define_action(self, subparsers: argparse._SubParsersAction) -> None:
        """
        Defines the CLI `configure` action.
        For each supported authenticator, sets whether it is used and adds the appropriate parameters.

        Args:
            subparsers (argparse._SubParsersAction): _description_
        """
        conf_parser: argparse.ArgumentParser = subparsers.add_parser('configure')
        self._common_actions_configuration(conf_parser)

        # Add the profile settings to the arguments
        ArkPydanticArgparse.schema_to_argparse(
            ArkProfile.schema(by_alias=False), conf_parser, ignore_keys=CONFIGURATION_IGNORED_DEFINITION_KEYS
        )

        # Add the supported authenticator settings and whether to work with them or not
        for authenticator in SUPPORTED_AUTHENTICATORS_LIST:
            conf_parser.add_argument(
                f'-ww{"".join([s[:2] for s in authenticator.authenticator_name().split("_")])}',
                f'--work-with-{authenticator.authenticator_name().replace("_", "-")}',
                action='store_true',
                help=f'Whether to work with {authenticator.authenticator_human_readable_name()} services',
            )
            if len(authenticator.supported_auth_methods()) > 1:
                conf_parser.add_argument(
                    f'-{"".join([s[:2] for s in authenticator.authenticator_name().split("_")])}am',
                    f'--{authenticator.authenticator_name().replace("_", "-")}-auth-method',
                    choices=[am.value for am in authenticator.supported_auth_methods()],
                    default=ArkAuthMethod.Default.value,
                )
            # Add the rest of the ark auth profile params
            ArkPydanticArgparse.schema_to_argparse(
                ArkAuthProfile.schema(by_alias=False),
                conf_parser,
                key_prefix=authenticator.authenticator_name().replace('_', '-'),
                ignore_keys=CONFIGURATION_IGNORED_DEFINITION_KEYS,
            )

            # Add the supported authentication methods settings of the authenticators
            for auth_method in authenticator.supported_auth_methods():
                auth_settings = ArkAuthMethodSettingsMap[auth_method]
                ArkPydanticArgparse.schema_to_argparse(
                    auth_settings.schema(by_alias=False),
                    conf_parser,
                    key_prefix=authenticator.authenticator_name().replace('_', '-'),
                    ignore_keys=CONFIGURATION_IGNORED_DEFINITION_KEYS
                    + CONFIGURATION_AUTHENTICATOR_IGNORED_DEFNITION_KEYS.get(authenticator.authenticator_name(), []),
                )

    def __run_interactive_action(self, args: argparse.Namespace) -> ArkProfile:
        """
        Performs an interactive configuration.
        The user is prompted for each Ark profile setting, with the default/defined CLI arguments.
        Selected authenticators are also configured with the user's auth methods and settings.

        Args:
            args (argparse.Namespace): _description_

        Returns:
            ArkProfile: _description_
        """
        # Load the profile first with the given profile name from the user
        profile_name = ArkArgsFormatter.get_arg(
            args, 'profile_name', 'Profile Name', ArkProfileLoader.deduce_profile_name(), prioritize_existing_val=True
        )
        profile = ArkProfileLoader.load_profile(profile_name) or ArkProfile(profile_name=profile_name)

        # Fill the rest of the profile settings
        profile_vals = ArkPydanticArgparse.argparse_to_schema_interactive(
            ArkProfile.schema(by_alias=False), args, ignored_keys=CONFIGURATION_IGNORED_INTERACTIVE_KEYS, existing_values=profile.dict()
        )
        profile = ArkPydanticArgparse.merge_by_model(ArkProfile, profile, profile_vals)
        if len(SUPPORTED_AUTHENTICATORS_LIST) == 1:
            work_with_authenticators = [SUPPORTED_AUTHENTICATORS_LIST[0].authenticator_human_readable_name()]
        else:
            work_with_authenticators = ArkArgsFormatter.get_checkbox_args(
                args,
                [f'work_with_{a.authenticator_name().replace("-", "_")}' for a in SUPPORTED_AUTHENTICATORS_LIST],
                'Which authenticators would you like to connect to',
                [a.authenticator_human_readable_name() for a in SUPPORTED_AUTHENTICATORS_LIST],
                {
                    f'work_with_{a.authenticator_name().replace("-", "_")}': a.authenticator_human_readable_name()
                    for a in SUPPORTED_AUTHENTICATORS_LIST
                    if a.authenticator_name() in profile.auth_profiles
                },
                True,
            )
        for idx, authenticator in enumerate(SUPPORTED_AUTHENTICATORS_LIST):
            # Find out if we are working with the authenticator
            auth_profile = profile.auth_profiles.get(authenticator.authenticator_name(), None) or ArkAuthProfile()
            if authenticator.authenticator_human_readable_name() in work_with_authenticators:
                # Get the authenticator auth method
                ArkArgsFormatter.print_success_bright(
                    ('\n' if idx != 0 else '') + f'◉ Configuring {authenticator.authenticator_human_readable_name()}',
                )
                if len(authenticator.supported_auth_methods()) > 1:
                    auth_method = ArkArgsFormatter.get_switch_arg(
                        args,
                        f'{authenticator.authenticator_name().replace("-", "_")}_auth_method',
                        'Authentication Method',
                        [ArkAuthMethodsDescriptionMap[m] for m in authenticator.supported_auth_methods()],
                        (
                            ArkAuthMethodsDescriptionMap[auth_profile.auth_method]
                            if authenticator.authenticator_name() in profile.auth_profiles
                            else ArkAuthMethodsDescriptionMap[authenticator.default_auth_method()[0]]
                        ),
                        prioritize_existing_val=True,
                    )
                    auth_method = next(
                        filter(lambda k: ArkAuthMethodsDescriptionMap[k] == auth_method, ArkAuthMethodsDescriptionMap.keys())
                    )
                    # If the default is chosen, override it by the authenticator's default
                    if auth_method == ArkAuthMethod.Default:
                        auth_method, _ = authenticator.default_auth_method()
                else:
                    auth_method, _ = authenticator.default_auth_method()
                ignored_keys = CONFIGURATION_IGNORED_INTERACTIVE_KEYS + CONFIGURATION_AUTHENTICATOR_IGNORED_INTERACTIVE_KEYS.get(
                    authenticator.authenticator_name(), []
                )
                # Get the auth profile general settings
                auth_profile_vals = ArkPydanticArgparse.argparse_to_schema_interactive(
                    ArkAuthProfile.schema(by_alias=False),
                    args,
                    ignored_keys=ignored_keys,
                    existing_values=auth_profile.dict(),
                    key_prefix=authenticator.authenticator_name(),
                )
                auth_profile = ArkPydanticArgparse.merge_by_model(
                    ArkAuthProfile,
                    auth_profile,
                    auth_profile_vals,
                    key_prefix=authenticator.authenticator_name(),
                    ignore_keys=['auth_method_settings'],
                )

                # Get the auth method settings and fill them
                method_settings = auth_profile.auth_method_settings
                if auth_method != auth_profile.auth_method:
                    method_settings = ArkAuthMethodSettingsMap[auth_method]()
                else:
                    method_settings = ArkAuthMethodSettingsMap[auth_method].parse_obj(auth_profile.auth_method_settings)
                method_settings_vals = ArkPydanticArgparse.argparse_to_schema_interactive(
                    method_settings.schema(by_alias=False),
                    args,
                    existing_values=method_settings.dict(),
                    override_aliases=CONFIGURATION_OVERRIDE_ALIASES,
                    key_prefix=authenticator.authenticator_name(),
                    ignored_keys=CONFIGURATION_IGNORED_INTERACTIVE_KEYS
                    + CONFIGURATION_AUTHENTICATOR_IGNORED_INTERACTIVE_KEYS.get(authenticator.authenticator_name(), []),
                    empty_allowed_keys=CONFIGURATION_ALLOWED_EMPTY_VALUES,
                    default_values=CONFIGURATION_AUTHENTICATORS_DEFAULTS,
                )

                # Finalize the auth profile
                auth_profile.auth_method = auth_method
                auth_profile.auth_method_settings = ArkPydanticArgparse.merge_by_model(
                    ArkAuthMethodSettingsMap[auth_method],
                    method_settings,
                    method_settings_vals,
                    key_prefix=authenticator.authenticator_name(),
                )
                profile.auth_profiles[authenticator.authenticator_name()] = auth_profile
            elif authenticator.authenticator_name() in profile.auth_profiles:
                del profile.auth_profiles[authenticator.authenticator_name()]
        return profile

    def __run_silent_action(self, args: argparse.Namespace) -> ArkProfile:
        """
        Runs the CLI configure action silently, without user interaction.

        Args:
            args (argparse.Namespace): _description_

        Raises:
            ArkException: _description_

        Returns:
            ArkProfile: _description_
        """
        # Load the profile based on the cli params and merge the rest of the params
        profile = ArkPydanticArgparse.merge_by_model(
            ArkProfile,
            ArkProfileLoader.load_profile(args.profile_name) or ArkProfile(profile_name=args.profile_name),
            ArkPydanticArgparse.argparse_to_schema(ArkProfile.schema(by_alias=False), args),
        )

        # Load the authenticators
        for authenticator in SUPPORTED_AUTHENTICATORS_LIST:
            auth_profile = profile.auth_profiles.get(authenticator.authenticator_name(), None) or ArkAuthProfile()
            if args.__dict__[f'work_with_{authenticator.authenticator_name()}']:
                if len(authenticator.supported_auth_methods()) > 1:
                    # Load the auth method
                    auth_method = ArkAuthMethod(args.__dict__[f'{authenticator.authenticator_name()}_auth_method'])

                    # If default, fallback to default auth method of the authenticator
                    if auth_method == ArkAuthMethod.Default:
                        auth_method, _ = authenticator.default_auth_method()
                else:
                    auth_method, _ = authenticator.default_auth_method()

                # Load the rest of the auth profile
                auth_profile = ArkPydanticArgparse.merge_by_model(
                    ArkAuthProfile,
                    auth_profile,
                    ArkPydanticArgparse.argparse_to_schema(
                        ArkAuthProfile.schema(by_alias=False), args, key_prefix=authenticator.authenticator_name()
                    ),
                    key_prefix=authenticator.authenticator_name(),
                )

                # Make sure if the type requires credentials, a username was supplied
                if auth_method in ArkAuthMethodsRequireCredentials and not auth_profile.username:
                    raise ArkException(f'Missing username for authenticator [{authenticator.authenticator_human_readable_name()}]')

                # Load the method settings
                method_settings = auth_profile.auth_method_settings
                if auth_method != auth_profile.auth_method:
                    method_settings = ArkAuthMethodSettingsMap[auth_method]()
                else:
                    method_settings = ArkAuthMethodSettingsMap[auth_method].parse_obj(method_settings)

                # Parse and merge the method settings from the cli
                method_settings_vals = ArkPydanticArgparse.argparse_to_schema(
                    method_settings.schema(by_alias=False), args, key_prefix=authenticator.authenticator_name()
                )

                # Remove the postfix
                method_settings_vals = {k.replace(f'{authenticator.authenticator_name()}_', ''): v for k, v in method_settings_vals.items()}

                # Finalize the auth profile
                auth_profile.auth_method = auth_method
                auth_profile.auth_method_settings = ArkPydanticArgparse.merge_by_model(
                    ArkAuthMethodSettingsMap[auth_method],
                    method_settings,
                    method_settings_vals,
                    key_prefix=authenticator.authenticator_name(),
                    defaults={
                        k.replace(f'{authenticator.authenticator_name()}_', ''): v
                        for k, v in CONFIGURATION_AUTHENTICATORS_DEFAULTS.items()
                        if k.startswith(f'{authenticator.authenticator_name()}_')
                    },
                )
                profile.auth_profiles[authenticator.authenticator_name()] = auth_profile
            elif authenticator.authenticator_name() in profile.auth_profiles:
                del profile.auth_profiles[authenticator.authenticator_name()]
        return profile

    @overrides
    def run_action(self, args: argparse.Namespace) -> None:
        """
        Runs the configure action.
        Prompts the user when interactive mode is run, based on the associated authenticators,
        and saves the configured profile when completed.

        Args:
            args (argparse.Namespace): _description_
        """
        # Parse the profile
        self._common_actions_execution(args)
        profile: Optional[ArkProfile] = None
        if ArkSystemConfig.is_interactive():
            profile = self.__run_interactive_action(args)
        else:
            profile = self.__run_silent_action(args)

        # Store it
        ArkProfileLoader.save_profile(profile)

        # Print out results
        ArkArgsFormatter.print_success(profile.json(indent=4))
        ArkArgsFormatter.print_success_bright(
            f"Profile has been saved to {ArkProfileLoader.profiles_folder()}",
        )

    @overrides
    def can_run_action(self, action_name: str, args: argparse.Namespace) -> bool:
        """
        Asserts the action is `configure`.

        Args:
            action_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
        return action_name == 'configure'
