import argparse
import json
import os
from fnmatch import fnmatch
from typing import List, Optional

import inquirer
from overrides import overrides

from ark_sdk_python.actions.ark_action import ArkAction
from ark_sdk_python.args import ArkArgsFormatter, ArkInquirerRender
from ark_sdk_python.models import ArkException, ArkProfile, ArkProfileLoader


class ArkProfilesAction(ArkAction):
    @overrides
    def define_action(self, subparsers: argparse._SubParsersAction) -> None:
        """
        Defines the CLI `profile` action, and adds actions for managing multiple profiles.

        Args:
            subparsers (argparse._SubParsersAction): _description_
        """
        profile_parser: argparse.ArgumentParser = subparsers.add_parser('profiles')
        self._common_actions_configuration(profile_parser)
        profile_cmd_subparsers = profile_parser.add_subparsers(dest="profile_cmd")
        profile_cmd_subparsers.required = True
        list_profiles_parser = profile_cmd_subparsers.add_parser('list', help='List all profiles')
        list_profiles_parser.add_argument('-n', '--name', help='Profile name to filter with by wildcard')
        list_profiles_parser.add_argument('-ap', '--auth-profile', help='Filter profiles by auth types')
        list_profiles_parser.add_argument(
            '-a', '--all', action='store_true', help='Whether to show all profiles data as well and not only their names'
        )
        show_profile_parser = profile_cmd_subparsers.add_parser('show', help='Show a profile')
        show_profile_parser.add_argument(
            '-pn', '--profile-name', required=False, help='Profile name to show, if not given, shows the current one'
        )
        delete_profile_parser = profile_cmd_subparsers.add_parser('delete', help='Delete a specific profile')
        delete_profile_parser.add_argument('-pn', '--profile-name', required=True, help='Profile name to delete')
        delete_profile_parser.add_argument('-y', '--yes', action='store_true', help='Whether to approve deletion non interactively')
        clear_profiles_parser = profile_cmd_subparsers.add_parser('clear', help='Clear all profiles')
        clear_profiles_parser.add_argument('-y', '--yes', action='store_true', help='Whether to approve clear non interactively')
        clone_profile_parser = profile_cmd_subparsers.add_parser('clone', help='Clones a profile')
        clone_profile_parser.add_argument('-pn', '--profile-name', required=True, help='Profile name to clone')
        clone_profile_parser.add_argument(
            '-npn', '--new-profile-name', help='New cloned profile name, if not given, will add _clone as part of the name'
        )
        clone_profile_parser.add_argument('-y', '--yes', action='store_true', help='Whether to override existing profile if exists')
        add_profile_parser = profile_cmd_subparsers.add_parser('add', help='Adds a profile to the profiles folder from a given path')
        add_profile_parser.add_argument('-pp', '--profile-path', required=True, help='Profile file path to be added')
        edit_profile_parser = profile_cmd_subparsers.add_parser('edit', help='Edits a profile interactively')
        edit_profile_parser.add_argument(
            '-pn', '--profile-name', required=False, help='Profile name to edit, if not given, edits the current one'
        )

    def __run_list_action(self, args: argparse.Namespace) -> None:
        # Start by loading all the profiles
        profiles: Optional[List[ArkProfile]] = ArkProfileLoader.load_all_profiles()
        if not profiles:
            ArkArgsFormatter.print_warning(
                'No profiles were found',
            )
            return
        # Filter profiles
        if args.name:
            profiles = [p for p in profiles if fnmatch(p.profile_name, args.name)]
        if args.auth_profile:
            profiles = [p for p in profiles if args.auth_profile in list(p.auth_profiles.keys())]
        # Print them based on request
        if args.all:
            ArkArgsFormatter.print_success(json.dumps([p.dict() for p in profiles], indent=4))
        else:
            ArkArgsFormatter.print_success(json.dumps([p.profile_name for p in profiles], indent=4))

    def __run_show_action(self, args: argparse.Namespace) -> None:
        profile_name = args.profile_name or ArkProfileLoader.deduce_profile_name()
        profile: Optional[ArkProfile] = ArkProfileLoader.load_profile(profile_name)
        if not profile:
            ArkArgsFormatter.print_warning(
                f'No profile was found for the name {profile_name}',
            )
            return
        ArkArgsFormatter.print_success(profile.json(indent=4))

    def __run_delete_action(self, args: argparse.Namespace) -> None:
        profile: Optional[ArkProfile] = ArkProfileLoader.load_profile(args.profile_name)
        if not profile:
            ArkArgsFormatter.print_warning(
                f'No profile was found for the name {args.profile_name}',
            )
            return
        if not args.yes:
            answer = inquirer.prompt(
                [inquirer.Confirm('answer', message=f'Are you sure you want to delete profile {args.profile_name}')],
                render=ArkInquirerRender(),
            )
            if not answer or not answer['answer']:
                return
        ArkProfileLoader.delete_profile(args.profile_name)

    def __run_clear_action(self, args: argparse.Namespace) -> None:
        if not args.yes:
            answer = inquirer.prompt(
                [inquirer.Confirm('answer', message='Are you sure you want to clear all profiles')], render=ArkInquirerRender()
            )
            if not answer or not answer['answer']:
                return
        ArkProfileLoader.clear_all_profiles()

    def __run_clone_action(self, args: argparse.Namespace) -> None:
        profile: Optional[ArkProfile] = ArkProfileLoader.load_profile(args.profile_name)
        if not profile:
            ArkArgsFormatter.print_warning(
                f'No profile was found for the name {args.profile_name}',
            )
            return
        cloned_profile: ArkProfile = profile.copy(update={'profile_name': args.new_profile_name or f'{profile.profile_name}_clone'})
        if ArkProfileLoader.profile_exists(cloned_profile.profile_name):
            if not args.yes:
                answer = inquirer.prompt(
                    [
                        inquirer.Confirm(
                            'answer', message=f'Are you sure you want to override existing profile {cloned_profile.profile_name}'
                        )
                    ],
                    render=ArkInquirerRender(),
                )
                if not answer or not answer['answer']:
                    return
        ArkProfileLoader.save_profile(cloned_profile)

    def __run_add_action(self, args: argparse.Namespace) -> None:
        if not os.path.exists(args.profile_path):
            ArkArgsFormatter.print_warning(
                f'Profile path [{args.profile_path}] does not exist, ignoring',
            )
            return
        try:
            profile: ArkProfile = ArkProfile.parse_file(args.profile_path)
            ArkProfileLoader.save_profile(profile)
        except Exception as ex:
            self._logger.exception(f'Failed to parser profile [{str(ex)}]')
            ArkArgsFormatter.print_failure(
                f'Profile path [{args.profile_path}] failed to be parsed, aborting',
            )
            return

    def __run_edit_action(self, args: argparse.Namespace) -> None:
        profile_name = args.profile_name or ArkProfileLoader.deduce_profile_name()
        profile: Optional[ArkProfile] = ArkProfileLoader.load_profile(profile_name)
        if not profile:
            ArkArgsFormatter.print_warning(
                f'No profile was found for the name {profile_name}',
            )
            return
        answer = inquirer.prompt(
            [inquirer.Editor('profile_edit', message=f'Chosen profile [{profile_name}] is about to be edited')],
            render=ArkInquirerRender(),
            answers={'profile_edit': profile.json(indent=4)},
        )
        edited_profile = ArkProfile.parse_raw(answer['profile_edit'])
        ArkProfileLoader.save_profile(edited_profile)

    @overrides
    def run_action(self, args: argparse.Namespace) -> None:
        """
        Runs the profile action.

        Args:
            args (argparse.Namespace): _description_

        Raises:
            ArkException: _description_
            ArkException: _description_
        """
        if args.profile_cmd == 'list':
            self.__run_list_action(args)
        elif args.profile_cmd == 'show':
            self.__run_show_action(args)
        elif args.profile_cmd == 'delete':
            self.__run_delete_action(args)
        elif args.profile_cmd == 'clear':
            self.__run_clear_action(args)
        elif args.profile_cmd == 'clone':
            self.__run_clone_action(args)
        elif args.profile_cmd == 'add':
            self.__run_add_action(args)
        elif args.profile_cmd == 'edit':
            self.__run_edit_action(args)
        else:
            raise ArkException(f'Invalid command {args.profile_cmd} given')

    @overrides
    def can_run_action(self, action_name: str, args: argparse.Namespace) -> bool:
        """
        Asserts the action is `profile`.

        Args:
            action_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
        return action_name == 'profiles'
