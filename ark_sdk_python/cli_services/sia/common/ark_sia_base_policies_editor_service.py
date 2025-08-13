import difflib
import itertools
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Final, Generic, List, Optional, Tuple, TypeVar

import inquirer

from ark_sdk_python.args.ark_args_formatter import ArkInquirerRender
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.ark_profile import ArkProfile, ArkProfileLoader
from ark_sdk_python.models.cli_services.sia.policies_editor.common import (
    ArkSIABaseGeneratePolicy,
    ArkSIACommitPolicies,
    ArkSIAEditPolicies,
    ArkSIAGetPoliciesStatus,
    ArkSIALoadedPolicies,
    ArkSIALoadPolicies,
    ArkSIAPoliciesDiff,
    ArkSIAPoliciesStatus,
    ArkSIARemovePolicies,
    ArkSIAResetPolicies,
    ArkSIAViewPolicies,
)
from ark_sdk_python.models.services.sia.policies.common import (
    ArkSIABaseAddPolicy,
    ArkSIABasePolicy,
    ArkSIABasePolicyListItem,
    ArkSIABaseUpdatePolicy,
    ArkSIADeletePolicy,
    ArkSIAGetPolicy,
)
from ark_sdk_python.services.ark_service import ArkService

MAX_LINE_DIFF: Final[int] = 100000

PolicyType = TypeVar('PolicyType', bound=ArkSIABasePolicy)
PolicyListItemType = TypeVar('PolicyListItemType', bound=ArkSIABasePolicyListItem)
AddPolicyType = TypeVar('AddPolicyType', bound=ArkSIABaseAddPolicy)
UpdatePolicyType = TypeVar('UpdatePolicyType', bound=ArkSIABaseUpdatePolicy)
GeneratePolicyType = TypeVar('GeneratePolicyType', bound=ArkSIABaseGeneratePolicy)


class ArkSIABasePoliciesEditorService(
    ArkService, ABC, Generic[PolicyType, PolicyListItemType, AddPolicyType, UpdatePolicyType, GeneratePolicyType]
):
    def __init__(
        self,
        policy_type: PolicyType,
        add_policy_type: AddPolicyType,
        update_policy_type: UpdatePolicyType,
        isp_auth: ArkISPAuth,
        policies_family: str,
        tenant_id: str,
        policies_cache_dir: Optional[str] = None,
        profile: Optional[ArkProfile] = None,
    ) -> None:
        super().__init__(isp_auth)
        profile = profile or ArkProfileLoader.load_default_profile()
        self._policies_family = policies_family
        self.__policies_cache_dir = Path(policies_cache_dir or Path.home() / '.ark_cache' / 'profiles' / profile.profile_name / tenant_id)
        if not policies_cache_dir and 'ARK_SIA_POLICIES_EDITOR_FOLDER' in os.environ:
            self.__policies_cache_dir = Path(os.environ['ARK_SIA_POLICIES_EDITOR_FOLDER'])
        self.__policies_cache_dir = self.__policies_cache_dir / policies_family
        self.__policies_cache_dir.mkdir(exist_ok=True, parents=True)
        self.__policy_type = policy_type
        self.__add_policy_type = add_policy_type
        self.__update_policy_type = update_policy_type

    @abstractmethod
    def _policy(self, get_policy: ArkSIAGetPolicy) -> PolicyType:
        pass

    @abstractmethod
    def _list_policies(self) -> List[PolicyListItemType]:
        pass

    @abstractmethod
    def _add_policy(self, add_policy: AddPolicyType) -> PolicyType:
        pass

    @abstractmethod
    def _update_policy(self, update_policy: UpdatePolicyType) -> PolicyType:
        pass

    @abstractmethod
    def _delete_policy(self, delete_policy: ArkSIADeletePolicy) -> None:
        pass

    @abstractmethod
    def _generate_policy(self, generate_policy: GeneratePolicyType, workspace_policies: List[PolicyType]) -> PolicyType:
        pass

    def __load_policy_diff(self, workspace_policy: PolicyType) -> Optional[Tuple[PolicyType, PolicyType]]:
        remote_policy = self._policy(ArkSIAGetPolicy(policy_id=str(workspace_policy.policy_id)))
        if remote_policy != workspace_policy:
            return (workspace_policy, remote_policy)
        return None

    def __load_policies_diff(self) -> Dict[str, Tuple[PolicyType, PolicyType]]:
        workspace_policies = self.__load_existing_policies_from_workspace()
        with ThreadPoolExecutor() as executor:
            remote_policies = {
                p[0].policy_name: p for p in executor.map(self.__load_policy_diff, workspace_policies.values()) if p is not None
            }
            return remote_policies

    def __load_policies_from_workspace_by_suffix(self, suffix: str = '') -> Dict[str, PolicyType]:
        p = Path(self.__policies_cache_dir).glob(f'*.json{suffix}')
        policies_files = [x for x in p if x.is_file() and x.suffix == suffix or '.json']
        policies = {}
        for f in policies_files:
            with open(f, 'r', encoding='utf-8') as fh:
                policy = self.__policy_type.model_validate_json(fh.read())
            policies[policy.policy_name] = policy
        return policies

    def __load_removed_policies_from_workspace(self) -> Dict[str, PolicyType]:
        return self.__load_policies_from_workspace_by_suffix('.removed')

    def __load_generated_policies_from_workspace(self) -> Dict[str, PolicyType]:
        return self.__load_policies_from_workspace_by_suffix('.generated')

    def __load_existing_policies_from_workspace(self) -> Dict[str, PolicyType]:
        return self.__load_policies_from_workspace_by_suffix()

    def __load_policy_to_workspace(self, policy: PolicyListItemType, override: bool) -> Optional[PolicyType]:
        policy_data = self._policy(ArkSIAGetPolicy(policy_id=policy.policy_id))
        policy_path = Path(self.__policies_cache_dir) / (policy_data.policy_name + '.json')
        if policy_path.exists():
            existing_data = self.__policy_type.model_validate_json(policy_path.read_text())
            if existing_data != policy_data:
                if not override:
                    return policy_data
        if not policy_data.policy_id:
            policy_data.policy_id = policy.policy_id
        policy_path.write_text(policy_data.model_dump_json(indent=4))
        (Path(self.__policies_cache_dir) / (policy_data.policy_name + '.json.removed')).unlink(missing_ok=True)

    def load_policies(self, load_policies: ArkSIALoadPolicies) -> ArkSIALoadedPolicies:
        """
        Loads all remote policies into the local workspace.
        The user is asked whether to overwrite existing policies that were edited either locally or remotely.
        When default overwrite is enabled, existing policies are overwritten without prompts.

        Args:
            load_policies (ArkSIALoadPolicies): _description_

        Returns:
            ArkSIALoadedPolicies: _description_
        """
        policies = self._list_policies()
        policies_to_query: Dict[str, PolicyType] = []
        with ThreadPoolExecutor() as executor:
            policies_to_query = {
                p.policy_name: p
                for p in executor.map(lambda p: self.__load_policy_to_workspace(p, load_policies.override), policies)
                if p is not None
            }
        # Build the query editor to ask the user
        policies_to_override = []
        if policies_to_query:
            answers = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        'override',
                        message=f'Conflicts detected, please choose if you wish to override local {self._policies_family} policies or leave them as is',
                        choices=[p.policy_name for p in policies_to_query.values()],
                    )
                ],
                render=ArkInquirerRender(),
            )
            if not answers:
                return
            policies_to_override = answers['override']
            for policy_name in policies_to_override:
                policy_path = Path(self.__policies_cache_dir) / (policy_name + '.json')
                if policy_path.exists() and policy_name in policies_to_query:
                    policy_path.write_text(policies_to_query[policy_name].model_dump_json(indent=4))
        return ArkSIALoadedPolicies(
            loaded_path=str(self.__policies_cache_dir),
            overall_policies_count=len(policies),
            loaded_policies_count=len(policies) - len(policies_to_query),
            overriden_policies_count=len(policies_to_override),
            untouched_policies_count=len(policies_to_query) - len(policies_to_override),
        )

    def edit_policies(self, edit_policies: ArkSIAEditPolicies) -> None:
        """
        Edits the set of specified policies one at a time, either via the CLI or the default OS editor.
        Edited policies are only saved locally until they are committed.

        Args:
            edit_policies (ArkSIAEditPolicies): _description_

        Raises:
            ArkServiceException: _description_
        """
        workspace_policies = self.__load_existing_policies_from_workspace()
        workspace_policies.update(self.__load_generated_policies_from_workspace())
        if not workspace_policies:
            raise ArkServiceException(
                f'No {self._policies_family} policies to edit in the workspace, please load the policies or generate a new one'
            )
        policy_names = edit_policies.names
        if not policy_names:
            answers = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        'names',
                        f'Which {self._policies_family} policies would you like to edit?, press space to select',
                        choices=[p.policy_name for p in workspace_policies.values()],
                    )
                ],
                render=ArkInquirerRender(),
            )
            if not answers:
                return
            policy_names = answers['names']
        try:
            answers = inquirer.prompt(
                [
                    inquirer.Editor(f'{name}_edit', message=f'Chosen {self._policies_family} policy [{name}] is about to be edited')
                    for name in policy_names
                ],
                render=ArkInquirerRender(),
                answers={f'{name}_edit': workspace_policies[name].model_dump_json(indent=4) for name in policy_names},
            )
            for name in policy_names:
                policy = self.__policy_type.model_validate_json(answers[f'{name}_edit'])
                for path in [
                    Path(self.__policies_cache_dir) / (name + '.json'),
                    Path(self.__policies_cache_dir) / (name + '.json.generated'),
                ]:
                    if path.exists():
                        path.write_text(policy.model_dump_json(indent=4))
                        break
        except Exception as ex:
            self._logger.error(
                f'An error occurred while trying to edit {self._policies_family} policies, '
                f'you can edit the policies at [{self.__policies_cache_dir}] [{str(ex)}]'
            )

    def remove_policies(self, remove_policies: ArkSIARemovePolicies) -> None:
        """
        Removes one or more policies from the local workspace.
        Until changes are committed, removing a remote policy only appends the `.deleted` indication to its name.
        After committing the changes, the policies are deleted both locally and remotely.
        New, uncommitted policies are deleted locally after the user consents.

        Args:
            remove_policies (ArkSIARemovePolicies): _description_

        Raises:
            ArkServiceException: _description_
        """
        workspace_policies = self.__load_existing_policies_from_workspace()
        workspace_policies.update(self.__load_generated_policies_from_workspace())
        if not workspace_policies:
            raise ArkServiceException(
                f'No {self._policies_family} policies to remove in the workspace, please load the policies or generate a new one'
            )
        policy_names = remove_policies.names
        if not policy_names:
            answers = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        'names',
                        f'Which {self._policies_family} policies would you like to remove?, press space to select',
                        choices=[p.policy_name for p in workspace_policies.values()],
                    )
                ],
                render=ArkInquirerRender(),
            )
            if not answers:
                return
            policy_names = answers['names']
        for policy_name in policy_names:
            for path in [
                Path(self.__policies_cache_dir) / (policy_name + '.json'),
                Path(self.__policies_cache_dir) / (policy_name + '.json.generated'),
            ]:
                if path.exists():
                    if path.suffix == '.json':
                        path.rename(Path(self.__policies_cache_dir) / (policy_name + '.json.removed'))
                    else:
                        answers = inquirer.prompt(
                            [
                                inquirer.Confirm(
                                    'remove',
                                    message=f'Are you sure you want to remove local {self._policies_family} policy [{policy_name}]?, removing an uncommitted local policy cannot be reverted',
                                )
                            ],
                            render=ArkInquirerRender(),
                        )
                        if not answers:
                            return
                        if answers['remove']:
                            path.unlink(missing_ok=True)

    def view_policies(self, view_policies: ArkSIAViewPolicies) -> None:
        """
        Allows the user to view one or more policies either together or individually, as defined in the CLI user prompt.
        Policies are viewed in the machine's default editor (both existing policies and newly generated policies).

        Args:
            view_policies (ArkSIAViewPolicies): _description_
        """
        workspace_policies = self.__load_existing_policies_from_workspace()
        workspace_policies.update(self.__load_generated_policies_from_workspace())
        policy_names = view_policies.names
        if not policy_names:
            answers = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        'names',
                        f'Which {self._policies_family} policies would you like to view?',
                        choices=[p.policy_name for p in workspace_policies.values()],
                    )
                ],
                render=ArkInquirerRender(),
            )
            if not answers:
                return
            policy_names = answers['names']
        if not policy_names:
            return
        try:
            if view_policies.unified:
                inquirer.prompt(
                    [inquirer.Editor('views', f'Show all selected {self._policies_family} policies')],
                    answers={
                        'views': '\n\n\n'.join(
                            [
                                f'# Policy [{policy_name}]\n{workspace_policies[policy_name].model_dump_json(indent=4)}'
                                for policy_name in policy_names
                            ]
                        )
                    },
                    render=ArkInquirerRender(),
                )
            else:
                inquirer.prompt(
                    [inquirer.Editor(f'{policy_name}_view', f'Show [{policy_name}]') for policy_name in policy_names],
                    render=ArkInquirerRender(),
                    answers={
                        f'{policy_name}_view': workspace_policies[policy_name].model_dump_json(indent=4) for policy_name in policy_names
                    },
                )
        except Exception as ex:
            self._logger.error(
                f'An error occurred while trying to view the {self._policies_family} policies, '
                f'you can view the policies at [{self.__policies_cache_dir}] [{str(ex)}]'
            )

    def reset_policies(self, reset_policy: ArkSIAResetPolicies) -> None:
        """
        Resets local workspace policies.
        When all policies are reset, all local policies are overwritten and deleted policies are removed.
        Otherwise, the user can select which policies are reset.
        This function does not alter newly generated uncommitted policies.

        Args:
            reset_policy (ArkSIAResetPolicies): _description_
        """
        if reset_policy.all:
            answers = inquirer.prompt(
                [inquirer.Confirm('reset', message=f'Are you sure you want to reset all edited {self._policies_family} policies?')]
            )
            if not answers:
                return
            if answers['reset']:
                self.load_policies(ArkSIALoadPolicies(override=True))
        else:
            policies_diff = self.__load_policies_diff()
            removed_policies = self.__load_removed_policies_from_workspace()
            if not policies_diff and not removed_policies:
                return
            policy_names = reset_policy.names
            if not policy_names:
                answers = inquirer.prompt(
                    [
                        inquirer.Checkbox(
                            'names',
                            f'Which {self._policies_family} policies would you like to reset?, press space to select',
                            choices=[p for p in policies_diff.keys() + removed_policies.keys()],
                        )
                    ],
                    render=ArkInquirerRender(),
                )
                if not answers:
                    return
                policy_names = answers['names']
            policy_names = [p for p in policy_names if p in policies_diff or p in removed_policies]
            for policy_name in policy_names:
                policy_path = Path(self.__policies_cache_dir) / (policy_name + '.json')
                if policy_name in policies_diff:
                    policy_path.write_text(policies_diff[policy_name][1].model_dump_json(indent=4))
                elif policy_name in removed_policies:
                    policy_path.write_text(removed_policies[policy_name].model_dump_json(indent=4))
                    (Path(self.__policies_cache_dir) / (policy_name + '.json.removed')).unlink(missing_ok=True)

    def generate_policy(self, generate_policy: GeneratePolicyType) -> None:
        """
        Generates a new policy from a template and the user's parameters.
        The user is prompted for the parameters when they are not specified in the CLI.
        After policy's parameters are defined, the policy is generates in memory and can bee edited.
        The new policy is saved locally until it is committed.

        Args:
            generate_policy (GeneratePolicyType): _description_
        """
        workspace_policies = self.__load_existing_policies_from_workspace()
        workspace_policies.update(self.__load_generated_policies_from_workspace())
        policy = self._generate_policy(generate_policy, workspace_policies)
        policy_path = Path(self.__policies_cache_dir) / (policy.policy_name + '.json.generated')
        # Let the user edit the generated policy
        if not generate_policy.disable_edit:
            try:
                answers = inquirer.prompt(
                    [
                        inquirer.Editor(
                            'policy_editor',
                            f'Newly {self._policies_family} policy is generated and ready to be edited, once edited, it will be saved to the local workspace',
                        )
                    ],
                    render=ArkInquirerRender(),
                    answers={'policy_editor': policy.model_dump_json(indent=4, exclude_none=True)},
                )
                if not answers:
                    return
                policy = self.__policy_type.model_validate_json(answers['policy_editor'])
            except Exception as ex:
                self._logger.error(
                    f'An error occurred while trying to edit the {self._policies_family} policy, '
                    f'the policy will be saved to [{policy_path}] and can be edited manually [{str(ex)}]'
                )
        policy_path.write_text(policy.model_dump_json(indent=4))

    def policies_diff(self, policies_diff: ArkSIAPoliciesDiff) -> None:
        """
        Calculates the diff between the local workspace and remote policies.
        This diff includes uncommitted removed policies. A unified or per policy diff can be displayed.

        Args:
            policies_diff (ArkSIAPoliciesDiff): _description_
        """
        loaded_policies_diff = self.__load_policies_diff()
        removed_policies = self.__load_removed_policies_from_workspace()
        if not loaded_policies_diff and not removed_policies:
            return
        if policies_diff.names:
            loaded_policies_diff = {k: v for k, v in loaded_policies_diff.items() if k in policies_diff.names}
            removed_policies = {k: v for k, v in removed_policies.items() if k in policies_diff.names}
        if not loaded_policies_diff and not removed_policies:
            return
        diffs = {
            policy_name: difflib.unified_diff(
                policy_tuple[1].model_dump_json(indent=4).splitlines(True),
                policy_tuple[0].model_dump_json(indent=4).splitlines(True),
                fromfile=f'local policy [{policy_name}]',
                tofile=f'remote policy [{policy_name}]',
                n=MAX_LINE_DIFF,
            )
            for policy_name, policy_tuple in loaded_policies_diff.items()
        }
        diffs.update(
            {
                policy_name: difflib.unified_diff(
                    policy.model_dump_json(indent=4).splitlines(True),
                    '',
                    fromfile=f'local policy [{policy_name}]',
                    tofile=f'remote policy [{policy_name}]',
                    n=MAX_LINE_DIFF,
                )
                for policy_name, policy in removed_policies.items()
            }
        )
        try:
            if policies_diff.unified:
                inquirer.prompt(
                    [inquirer.Editor('diffs', 'Show all diffs')],
                    render=ArkInquirerRender(),
                    answers={'diffs': '\n\n\n'.join([''.join(d) for d in diffs.values()])},
                )
            else:
                inquirer.prompt(
                    [inquirer.Editor(f'{policy_name}_diff', f'Show [{policy_name}] diff') for policy_name in diffs.keys()],
                    render=ArkInquirerRender(),
                    answers={f'{policy_name}_diff': ''.join(policy_diffs) for policy_name, policy_diffs in diffs.items()},
                )
        except Exception as ex:
            self._logger.error(
                f'An error occurred while trying to show {self._policies_family} policies diff, '
                f'you can view the policies at [{self.__policies_cache_dir}] [{str(ex)}]'
            )

    def policies_status(self, get_policies_status: ArkSIAGetPoliciesStatus) -> ArkSIAPoliciesStatus:
        """
        Gets the status of locally altered policies.

        Args:
            get_policies_status (ArkSIAGetPoliciesStatus): _description_

        Returns:
            ArkSIAPoliciesStatus: _description_
        """
        loaded_policies_diff = self.__load_policies_diff()
        removed_policies = self.__load_removed_policies_from_workspace()
        generated_policies = self.__load_generated_policies_from_workspace()
        if get_policies_status.names:
            loaded_policies_diff = {k: v for k, v in loaded_policies_diff.items() if k in get_policies_status.names}
            removed_policies = {k: v for k, v in removed_policies.items() if k in get_policies_status.names}
            generated_policies = {k: v for k, v in generated_policies.items() if k in get_policies_status.names}
        return ArkSIAPoliciesStatus(
            modified_policies=list(loaded_policies_diff.keys()),
            removed_policies=list(removed_policies.keys()),
            added_policies=list(generated_policies.keys()),
        )

    def commit_policies(self, commit_policies: ArkSIACommitPolicies) -> None:
        """
        Commits policies.
        The function first calculates the differences between the local and remote policies to find out which policies were edited, including
        the policies selected for deletion and new, uncommitted policies. It also
        allows selecting whether to commit all the edited policies or only specific policies by name.
        After all policies are committed, the workspace is reorganized accordingly.

        Args:
            commit_policies (ArkSIACommitPolicies): _description_
        """
        loaded_policies_diff = self.__load_policies_diff()
        removed_policies = self.__load_removed_policies_from_workspace()
        generated_policies = self.__load_generated_policies_from_workspace()
        if not loaded_policies_diff and not removed_policies and not generated_policies:
            return
        if commit_policies.all:
            answers = inquirer.prompt(
                [inquirer.Confirm('reset', message=f'Are you sure you want to commit all edited {self._policies_family} policies?')]
            )
            if not answers or not answers['reset']:
                return
        else:
            if commit_policies.names:
                loaded_policies_diff = {k: v for k, v in loaded_policies_diff.items() if k in commit_policies.names}
                removed_policies = {k: v for k, v in removed_policies.items() if k in commit_policies.names}
                generated_policies = {k: v for k, v in generated_policies.items() if k in commit_policies.names}
            else:
                answers = inquirer.prompt(
                    [
                        inquirer.Checkbox(
                            'names',
                            f'Which {self._policies_family} policies would you like to commit?, press space to select',
                            choices=list(loaded_policies_diff.keys()) + list(removed_policies.keys()) + list(generated_policies.keys()),
                        )
                    ],
                    render=ArkInquirerRender(),
                )
                if not answers:
                    return
                loaded_policies_diff = {k: v for k, v in loaded_policies_diff.items() if k in answers['names']}
                removed_policies = {k: v for k, v in removed_policies.items() if k in answers['names']}
                generated_policies = {k: v for k, v in generated_policies.items() if k in answers['names']}
            if not loaded_policies_diff and not removed_policies and not generated_policies:
                return
        with ThreadPoolExecutor() as executor:
            added = executor.map(lambda p: self._add_policy(self.__add_policy_type(**p.model_dump())), generated_policies.values())
            updated = executor.map(
                lambda p: self._update_policy(self.__update_policy_type(**p[0].model_dump())), loaded_policies_diff.values()
            )
            deleted = executor.map(
                lambda p: self._delete_policy(ArkSIADeletePolicy(policy_id=p.policy_id, policy_name=p.policy_name)),
                removed_policies.values(),
            )
            # Loop for exception checking
            added_policies = list(added)
            for _ in itertools.chain(updated, deleted):
                pass
        for policy_name in removed_policies.keys():
            (Path(self.__policies_cache_dir) / (policy_name + '.json.removed')).unlink(missing_ok=True)
        for policy_name in generated_policies.keys():
            for policy in added_policies:
                if policy.policy_name == policy_name:
                    (Path(self.__policies_cache_dir) / (policy_name + '.json.generated')).rename(
                        (Path(self.__policies_cache_dir) / (policy_name + '.json'))
                    )
                    (Path(self.__policies_cache_dir) / (policy_name + '.json')).write_text(policy.model_dump_json(indent=4))
