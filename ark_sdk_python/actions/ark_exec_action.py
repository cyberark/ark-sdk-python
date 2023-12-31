import argparse
import itertools
import json
import os
import traceback
from abc import abstractmethod
from collections import namedtuple
from typing import Any, Dict, Generator, List, Optional, Tuple, Type, Union

from overrides import overrides
from retry.api import retry_call

from ark_sdk_python.actions.ark_action import ArkAction
from ark_sdk_python.args import ArkArgsFormatter, ArkPydanticArgparse
from ark_sdk_python.auth import SUPPORTED_AUTHENTICATORS
from ark_sdk_python.auth.ark_auth import ArkAuth
from ark_sdk_python.cli_services import ArkCLIAPI
from ark_sdk_python.common import ArkAsyncRequest, ArkPollers, ArkSystemConfig
from ark_sdk_python.models import ArkException, ArkModel
from ark_sdk_python.models.ark_model import ArkPollableModel
from ark_sdk_python.models.ark_profile import ArkProfileLoader
from ark_sdk_python.services.ark_service import ArkService


class ArkExecAction(ArkAction):
    def _serialize_output(self, output: Optional[Union[List, Dict, ArkModel, Generator, Tuple, Any]]) -> str:
        if output is None:
            return ''
        if isinstance(output, Generator):
            return self._serialize_output(list(itertools.chain.from_iterable([p.items for p in output])))
        if isinstance(output, list):
            return json.dumps(
                [json.loads(a.json(by_alias=False, exclude={'poll_progress_callback'})) for a in output if a is not None], indent=4
            )
        elif isinstance(output, tuple):
            return json.dumps(
                [json.loads(a.json(by_alias=False, exclude={'poll_progress_callback'})) for a in output if a is not None], indent=4
            )
        elif isinstance(output, dict):
            return json.dumps(
                {
                    k: json.loads(v.json(indent=4, by_alias=False, exclude={'poll_progress_callback'}))
                    for k, v in output.items()
                    if k is not None and v is not None
                },
                indent=4,
            )
        elif issubclass(type(output), ArkModel):
            return output.json(indent=4, by_alias=False, exclude={'poll_progress_callback'})
        elif issubclass(type(output), ArkAsyncRequest):
            return output.async_task.json(indent=4, by_alias=False)
        return str(output)

    def _write_output_to_file(self, output_path: str, serialized_output: str) -> None:
        output_path = os.path.abspath(output_path)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(serialized_output)

    def _run_async_action(
        self, service: ArkService, schemas_map: Dict[str, Optional[Type[ArkModel]]], action: str, args: argparse.Namespace
    ) -> None:
        try:
            model_type: Type[ArkPollableModel] = schemas_map[action.replace('_', '-')]
            model: ArkPollableModel = model_type.parse_obj(ArkPydanticArgparse.argparse_to_schema(model_type.schema(), args))
            model.poll_progress_callback = ArkPollers.default_poller()
            output = getattr(service, action.replace('-', '_'))(model)
            async_req = None
            if issubclass(type(output), ArkAsyncRequest):
                async_req = output
            elif isinstance(output, tuple):
                for a in output:
                    if issubclass(type(a), ArkAsyncRequest):
                        async_req = a
                        break
            if async_req is not None:
                if args.output_path:
                    self._write_output_to_file(
                        args.output_path, async_req.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})
                    )
                if async_req.task_failed():
                    if async_req.task_timeout():
                        ArkArgsFormatter.print_warning(
                            f'Failed to execute async command due to timeout, error:\n{async_req.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                        )
                        raise ArkException(
                            f'Failed to execute async command due to timeout, error:\n{async_req.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                        )
                    else:
                        ArkArgsFormatter.print_failure(
                            f'Failed to execute async command, error:\n{async_req.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                        )
                        raise ArkException(
                            f'Failed to execute async command, error:\n{async_req.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                        )
                else:
                    ArkArgsFormatter.print_success(self._serialize_output(output))
            elif isinstance(output, list) and all(issubclass(type(ar), ArkAsyncRequest) for ar in output):
                if args.output_path:
                    self._write_output_to_file(
                        args.output_path,
                        json.dumps([ar.async_task.dict(indent=4, by_alias=False, exclude={"poll_progress_callback"}) for ar in output]),
                    )
                for ar in output:
                    if ar.task_failed():
                        if ar.task_timeout():
                            ArkArgsFormatter.print_warning(
                                f'Failed to execute async command due to timeout, error:\n{ar.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                            )
                            raise ArkException(
                                f'Failed to execute async command due to timeout, error:\n{ar.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                            )
                        else:
                            ArkArgsFormatter.print_failure(
                                f'Failed to execute async command, error:\n{ar.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                            )
                            raise ArkException(
                                f'Failed to execute async command, error:\n{ar.async_task.json(indent=4, by_alias=False, exclude={"poll_progress_callback"})}',
                            )
                    else:
                        ArkArgsFormatter.print_success(self._serialize_output(ar))
            elif output is not None:
                ArkArgsFormatter.print_success(self._serialize_output(output))
        except Exception as ex:
            self._logger.exception(f'Failed running async command {action}')
            ArkArgsFormatter.print_failure(f'Failed to execute async command, error:\n{str(ex)}')
            self._logger.debug(traceback.format_exc())
            raise ex

    def _run_sync_action(
        self, service: ArkService, schemas_map: Dict[str, Optional[Type[ArkModel]]], action: str, args: argparse.Namespace
    ) -> None:
        try:
            model_type: Type[ArkPollableModel] = schemas_map[action.replace('_', '-')]
            if model_type:
                model: ArkModel = model_type.parse_obj(ArkPydanticArgparse.argparse_to_schema(model_type.schema(), args))
                output = getattr(service, action.replace('-', '_'))(model)
            else:
                output = getattr(service, action.replace('-', '_'))()
            if output is not None:
                serialized_output: str = self._serialize_output(output)
                if args.output_path:
                    self._write_output_to_file(args.output_path, serialized_output)
                ArkArgsFormatter.print_success(serialized_output)
            else:
                ArkArgsFormatter.print_success(f'{action.replace("-", " ").title()} finished successfully')
        except Exception as ex:
            self._logger.exception(f'Failed running command {action}')
            ArkArgsFormatter.print_failure(f'Failed to execute command, error:\n{str(ex)}')
            self._logger.debug(traceback.format_exc())
            raise ex

    def _define_actions_by_schemas(
        self,
        subparsers: argparse._SubParsersAction,
        schemas_map: Dict[str, Optional[Type[ArkModel]]],
        defaults_map: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        for action, schema in schemas_map.items():
            parser = subparsers.add_parser(action)
            if schema:
                ArkPydanticArgparse.schema_to_argparse(
                    schema.schema(), parser, defaults=defaults_map.get(action, None) if defaults_map else None
                )

    @overrides
    def define_action(self, subparsers: argparse._SubParsersAction) -> None:
        """
        Defines the CLI `exec` action, with its subparsers (args) for the service.

        Args:
            subparsers (argparse._SubParsersAction): _description_
        """
        exec_parser = None
        exec_subparsers = None
        # Check if the exec subparser already exists from previous definitions of a service
        if 'exec' in subparsers._name_parser_map.keys():  # pylint: disable=protected-access
            # Retrieve the existing exec parser
            exec_parser = subparsers._name_parser_map['exec']  # pylint: disable=protected-access
            exec_subparsers = exec_parser._subparsers._group_actions[0]  # pylint: disable=protected-access
        else:
            # Create a new exec parser
            exec_parser = subparsers.add_parser('exec')
            self._common_actions_configuration(exec_parser)
            exec_parser.add_argument('-pn', '--profile-name', default=ArkProfileLoader.default_profile_name(), help='Profile name to load')
            exec_parser.add_argument('-op', '--output-path', help='Output file to write data to')
            exec_parser.add_argument('-rf', '--request-file', help='Request file containing the parameters for the exec action')
            exec_parser.add_argument('-rc', '--retry-count', type=int, help='Retry count for execution', default=1)
            exec_parser.add_argument(
                '-ra',
                '--refresh-auth',
                action='store_true',
                help='If possible, will try to refresh the active authentication before running the actual command',
            )
            exec_subparsers = exec_parser.add_subparsers(dest="command")
            exec_subparsers.required = True
        self.define_exec_action(exec_subparsers)

    @overrides
    def run_action(self, args: argparse.Namespace) -> None:
        """
        Runs the exec action.
        Loads the authenticators from the cache and connects to the API using the loaded authenticators.
        Each service is created from the API, based on the given authenticators, and then
        runs the exec action using the API.

        Args:
            args (argparse.Namespace): _description_

        Raises:
            ArkException: _description_
            ArkException: _description_
        """
        self._common_actions_execution(args)
        profile = ArkProfileLoader.load_profile(ArkProfileLoader.deduce_profile_name(args.profile_name))
        if not profile:
            raise ArkException('Please configure a profile and login before trying to exec')

        # Load token from cache for each auth profile
        authenticators: List[ArkAuth] = []
        for authenticator_name in profile.auth_profiles.keys():
            authenticator = SUPPORTED_AUTHENTICATORS[authenticator_name]()
            if not authenticator.load_authentication(profile, args.refresh_auth):
                continue
            authenticators.append(authenticator)

        if len(authenticators) == 0:
            raise ArkException(
                'Failed to load authenticators, tokens are either expired or authenticators are not logged in, please login first'
            )
        if len(authenticators) != len(profile.auth_profiles) and ArkSystemConfig.is_interactive():
            ArkArgsFormatter.print_colored('Not all authenticators are logged in, some of the functionality will be disabled')

        # Create the CLI API with the authenticators
        api = ArkCLIAPI(authenticators, profile)

        # Run the actual exec fitting action with the api
        # Run it with retries as per defined by user
        retry_call(
            self.run_exec_action,
            fargs=[api, args],
            tries=args.retry_count,
            delay=1,
            logger=namedtuple("logger", ("warning"))(
                warning=lambda _1, _2, delay: ArkArgsFormatter.print_failure(f"Retrying in {delay} seconds")
            ),
        )

    @overrides
    def can_run_action(self, action_name: str, args: argparse.Namespace) -> bool:
        """
        Asserts the action is `exec`.

        Args:
            action_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
        return action_name == 'exec' and self.can_run_exec_action(args.command, args)

    @abstractmethod
    def define_exec_action(self, exec_subparsers: argparse._SubParsersAction) -> None:
        """
        Defines an exec action, and its specified configurations and args, for a service.

        Args:
            exec_subparsers (argparse._SubParsersAction): _description_
        """

    @abstractmethod
    def run_exec_action(self, api: ArkCLIAPI, args: argparse.Namespace) -> None:
        """
        Runs the exec action for a service with the specified arguments and API.

        Args:
            api (ArkCLIAPI): _description_
            args (argparse.Namespace): _description_
        """

    @abstractmethod
    def can_run_exec_action(self, command_name: str, args: argparse.Namespace) -> bool:
        """
        Checks whether the specified exec service action can be run.

        Args:
            command_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
