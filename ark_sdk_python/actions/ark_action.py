import argparse
import os
from abc import ABC, abstractmethod

from ark_sdk_python.common import ArkSystemConfig, get_logger
from ark_sdk_python.models import ArkProfileLoader


class ArkAction(ABC):
    def __init__(self):
        self._logger = get_logger(app=self.__class__.__name__)

    def _common_actions_configuration(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-r', '--raw', action='store_true', help='Whether to raw output')
        parser.add_argument('-s', '--silent', action='store_true', help='Silent execution, no interactiveness')
        parser.add_argument('-ao', '--allow-output', action='store_true', help='Allow stdout / stderr even when silent and not interactive')
        parser.add_argument('-v', '--verbose', action='store_true', help='Whether to verbose log')
        parser.add_argument('-ls', '--logger-style', choices=['default'], help='Which verbose logger style to use', default='default')
        parser.add_argument(
            '-ll',
            '--log-level',
            help='Log level to use while verbose',
            choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
            default='INFO',
        )
        parser.add_argument(
            '-dcv', '--disable-cert-verification', action='store_true', help='Disables certificate verification on HTTPS calls, unsafe!'
        )
        parser.add_argument('-tc', '--trusted-cert', help='Certificate to use for HTTPS calls')

    def _common_actions_execution(self, args: argparse.Namespace) -> None:
        ArkSystemConfig.enable_color()
        ArkSystemConfig.enable_interactive()
        ArkSystemConfig.disable_verbose_logging()
        ArkSystemConfig.disallow_output()
        ArkSystemConfig.set_logger_style(args.logger_style)
        ArkSystemConfig.enable_certificate_verification()
        if args.raw:
            ArkSystemConfig.disable_color()
        if args.silent:
            ArkSystemConfig.disable_interactive()
        if args.verbose:
            ArkSystemConfig.enable_verbose_logging(args.log_level)
        if args.allow_output:
            ArkSystemConfig.allow_output()
        if args.disable_cert_verification:
            ArkSystemConfig.disable_certificate_verification()
        elif args.trusted_cert is not None:
            ArkSystemConfig.set_trusted_certificate(args.trusted_cert)
        self._logger = get_logger(app=self.__class__.__name__)
        if 'profile-name' in args:
            args.profile_name = ArkProfileLoader.deduce_profile_name(args.profile_name)
        if 'DEPLOY_ENV' not in os.environ:
            # Last fallback on deploy env
            os.environ['DEPLOY_ENV'] = 'prod'

    @abstractmethod
    def define_action(self, subparsers: argparse._SubParsersAction) -> None:
        """
        Defines the action as part of the specified subparsers group.

        Args:
            subparsers (argparse._SubParsersAction): _description_
        """

    @abstractmethod
    def run_action(self, args: argparse.Namespace) -> None:
        """
        Runs the actual action with the given arguments.

        Args:
            args (argparse.Namespace): _description_
        """

    @abstractmethod
    def can_run_action(self, action_name: str, args: argparse.Namespace) -> bool:
        """
        Checks whether the given action can be run with the specified arguments.

        Args:
            action_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
