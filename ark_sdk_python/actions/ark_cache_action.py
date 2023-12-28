import argparse
import os

from overrides import overrides

from ark_sdk_python.actions.ark_action import ArkAction
from ark_sdk_python.args import ArkArgsFormatter
from ark_sdk_python.common.ark_keyring import ARK_BASIC_KEYRING_FOLDER_ENV_VAR, DEFAULT_BASIC_KEYRING_FOLDER, ArkKeyring, BasicKeyring
from ark_sdk_python.models import ArkException


class ArkCacheAction(ArkAction):
    @overrides
    def define_action(self, subparsers: argparse._SubParsersAction) -> None:
        """
        Defines the CLI `cache` action, and adds the clear cache function.

        Args:
            subparsers (argparse._SubParsersAction): _description_
        """
        cache_parser: argparse.ArgumentParser = subparsers.add_parser('cache')
        self._common_actions_configuration(cache_parser)
        cache_cmd_subparsers = cache_parser.add_subparsers(dest="cache_cmd")
        cache_cmd_subparsers.required = True
        cache_cmd_subparsers.add_parser('clear', help='Clears all profiles cache')

    def __run_clear_cache_action(self) -> None:
        if isinstance(ArkKeyring.get_keyring(), BasicKeyring):
            cache_folder_path = os.path.join(os.path.expanduser('~'), DEFAULT_BASIC_KEYRING_FOLDER)
            if ARK_BASIC_KEYRING_FOLDER_ENV_VAR in os.environ:
                cache_folder_path = os.environ[ARK_BASIC_KEYRING_FOLDER_ENV_VAR]
            os.unlink(f'{cache_folder_path}{os.sep}keyring')
            os.unlink(f'{cache_folder_path}{os.sep}mac')
        else:
            ArkArgsFormatter.print_normal('Cache clear is only valid for basic keyring implementation at the moment')

    @overrides
    def run_action(self, args: argparse.Namespace) -> None:
        """
        Runs the cache action.

        Args:
            args (argparse.Namespace): _description_

        Raises:
            ArkException: _description_
        """
        if args.cache_cmd == 'clear':
            self.__run_clear_cache_action()
        else:
            raise ArkException(f'Invalid command {args.profile_cmd} given')

    @overrides
    def can_run_action(self, action_name: str, args: argparse.Namespace) -> bool:
        """
        Asserts the action is `cache`.

        Args:
            action_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
        return action_name == 'cache'
