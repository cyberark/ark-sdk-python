import argparse
from typing import List, Optional, Tuple

from overrides import overrides

from ark_sdk_python.actions.ark_exec_action import ArkExecAction
from ark_sdk_python.cli_services import ArkCLIAPI
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.actions.services import SUPPORTED_SERVICE_ACTIONS


class ArkServiceExecAction(ArkExecAction):
    def __define_service_exec_action(
        self,
        action_def: ArkServiceActionDefinition,
        subparsers: argparse._SubParsersAction,
        parent_actions_def: Optional[List[ArkServiceActionDefinition]] = None,
    ) -> argparse._SubParsersAction:
        action_parser = subparsers.add_parser(action_def.action_name)
        action_dest = action_def.action_name
        if parent_actions_def:
            action_dest = '_'.join([p.action_name for p in parent_actions_def]) + f'_{action_def.action_name}'
        action_subparsers = action_parser.add_subparsers(dest=f"{action_dest}_action")
        action_subparsers.required = True
        if action_def.schemas:
            self._define_actions_by_schemas(action_subparsers, action_def.schemas, action_def.defaults)
        return action_subparsers

    def __define_service_exec_actions(
        self,
        action_def: ArkServiceActionDefinition,
        subparsers: argparse._SubParsersAction,
        parent_actions_def: Optional[List[ArkServiceActionDefinition]] = None,
    ) -> None:
        action_subparsers = self.__define_service_exec_action(action_def, subparsers, parent_actions_def)
        if action_def.subactions:
            for subaction in action_def.subactions:
                self.__define_service_exec_actions(
                    subaction, action_subparsers, parent_actions_def + [action_def] if parent_actions_def else [action_def]
                )

    def __deduce_action_def(
        self,
        args: argparse.Namespace,
        action_def: ArkServiceActionDefinition,
        parent_actions_def: Optional[List[ArkServiceActionDefinition]] = None,
    ) -> Tuple[ArkServiceActionDefinition, str]:
        action_dest = f'{action_def.action_name}_action'
        if parent_actions_def:
            action_dest = '_'.join([p.action_name for p in parent_actions_def]) + f'_{action_def.action_name}_action'
        if action_dest in args.__dict__:
            action_value = args.__dict__[action_dest]
            if action_def.subactions:
                for subaction in action_def.subactions:
                    if subaction.action_name == action_value:
                        return self.__deduce_action_def(
                            args, subaction, parent_actions_def + [action_def] if parent_actions_def else [action_def]
                        )
            return action_def, action_dest

    def __deduce_action_command_def(self, command_name: str, args: argparse.Namespace) -> Tuple[ArkServiceActionDefinition, str]:
        for action_def in SUPPORTED_SERVICE_ACTIONS:
            if action_def.action_name == command_name:
                # Find the fitting action
                return self.__deduce_action_def(args, action_def)

    @overrides
    def define_exec_action(self, exec_subparsers: argparse._SubParsersAction) -> None:
        """
        Defines all the supported service actions as CLI actions, with its associated arguments and schemas.

        Args:
            exec_subparsers (argparse._SubParsersAction): _description_
        """
        for actions in SUPPORTED_SERVICE_ACTIONS:
            self.__define_service_exec_actions(actions, exec_subparsers)

    @overrides
    def run_exec_action(self, api: ArkCLIAPI, args: argparse.Namespace) -> None:
        """
        Deduces from the arguments the appropriate service definition and action.
        Finds the appropriate service using the definition and executes the sync or async service action.

        Args:
            api (ArkCLIAPI): _description_
            args (argparse.Namespace): _description_
        """
        action_def, action_dest = self.__deduce_action_command_def(args.command, args)
        action_value = args.__dict__[action_dest]
        api_name = action_dest.replace('_action', '')
        # cli sub-commands use dashes, but function names use underscores
        api_name = api_name.replace('-', '_')
        while '_' in api_name and not hasattr(api, api_name):
            api_name = api_name.rsplit('_', 1)[0]
        service = getattr(api, api_name)
        if action_def.async_actions and action_value in action_def.async_actions:
            self._run_async_action(service, action_def.schemas, action_value, args)
        else:
            self._run_sync_action(service, action_def.schemas, action_value, args)

    @overrides
    def can_run_exec_action(self, command_name: str, args: argparse.Namespace) -> bool:
        """
        Checks whether there is a service definition for the command and its actions.

        Args:
            command_name (str): _description_
            args (argparse.Namespace): _description_

        Returns:
            bool: _description_
        """
        return self.__deduce_action_command_def(command_name, args) is not None
