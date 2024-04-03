from datetime import date, timedelta
from typing import Dict, Final, List, Optional

import inquirer
from overrides import overrides

from ark_sdk_python.args.ark_args_formatter import ArkInquirerRender
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.cli_services.dpa.common.ark_dpa_base_policies_editor_service import ArkDPABasePoliciesEditorService
from ark_sdk_python.models.ark_profile import ArkProfile
from ark_sdk_python.models.cli_services.dpa.policies_editor.vm import ArkDPAVMGeneratePolicy
from ark_sdk_python.models.common import ArkProtocolType, ArkWorkspaceType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.policies.common import ArkDPADeletePolicy, ArkDPAGetPolicy, ArkDPARuleStatus, ArkDPAUserData
from ark_sdk_python.models.services.dpa.policies.vm import (
    ArkDPAVMAddPolicy,
    ArkDPAVMAuthorizationRule,
    ArkDPAVMAWSProviderData,
    ArkDPAVMAzureProviderData,
    ArkDPAVMConnectionDataType,
    ArkDPAVMConnectionInformation,
    ArkDPAVMFQDNOperator,
    ArkDPAVMFQDNRule,
    ArkDPAVMGCPProviderData,
    ArkDPAVMLocalEphemeralUserConnectionMethodData,
    ArkDPAVMOnPremProviderData,
    ArkDPAVMPolicy,
    ArkDPAVMPolicyListItem,
    ArkDPAVMProvider,
    ArkDPAVMRDPLocalEphemeralUserConnectionData,
    ArkDPAVMUpdatePolicy,
)
from ark_sdk_python.services.dpa.policies.vm.ark_dpa_vm_policies_service import ArkDPAVMPoliciesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-policies-vm-editor', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
DEFAULT_GENERATED_POLICY: Final[ArkDPAVMPolicy] = ArkDPAVMPolicy(
    policy_name='Default VM Policy',
    status=ArkDPARuleStatus.Draft,
    description='Auto generated vm policy',
    providers_data={},
    start_date=date.today().strftime('%Y-%m-%d'),
    end_date=(date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
    user_access_rules=[],
)
DEFAULT_GENERATED_AUTHORIZATION_RULE: Final[ArkDPAVMAuthorizationRule] = ArkDPAVMAuthorizationRule(
    rule_name='Default VM Rule',
    user_data=ArkDPAUserData(roles=['DpaAdmin'], groups=[], users=[]),
    connection_information=ArkDPAVMConnectionInformation(
        connect_as={},
        grant_access=2,
        idle_time=10,
        days_of_week=[],
        full_days=True,
        hours_from='07:00',
        hours_to='17:00',
        time_zone='Asia/Jerusalem',
    ),
)
DEFAULT_GENERATED_PROVIDERS: Final[Dict[ArkWorkspaceType, ArkDPAVMProvider]] = {
    ArkWorkspaceType.AWS: ArkDPAVMAWSProviderData(regions=[], tags=[{'key': 'value'}], vpc_ids=[], account_ids=[]),
    ArkWorkspaceType.AZURE: ArkDPAVMAzureProviderData(
        regions=[], tags=[{'key': 'value'}], resource_groups=[], vnet_ids=[], subscriptions=[]
    ),
    ArkWorkspaceType.GCP: ArkDPAVMGCPProviderData(regions=[], tags=[{'key': 'value'}], network_ids=[], projects=[]),
    ArkWorkspaceType.ONPREM: ArkDPAVMOnPremProviderData(
        fqdn_rules=[ArkDPAVMFQDNRule(operator=ArkDPAVMFQDNOperator.WILDCARD, computername_pattern='*', domain='default.com')],
    ),
}
DEFAULT_GENERATED_PROTOCOLS: Final[Dict[ArkProtocolType, ArkDPAVMConnectionDataType]] = {
    ArkProtocolType.SSH: 'root',
    ArkProtocolType.RDP: ArkDPAVMRDPLocalEphemeralUserConnectionData(
        local_ephemeral_user=ArkDPAVMLocalEphemeralUserConnectionMethodData(assign_groups={'Administrators'})
    ),
}
SUPPORTED_SSH_PROTOCOL_PROVIDERS: Final[ArkWorkspaceType] = [
    ArkWorkspaceType.AWS,
    ArkWorkspaceType.AZURE,
    ArkWorkspaceType.GCP,
    ArkWorkspaceType.ONPREM,
]
SUPPORTED_RDP_PROTOCOL_PROVIDERS: Final[ArkWorkspaceType] = [ArkWorkspaceType.AWS, ArkWorkspaceType.AZURE, ArkWorkspaceType.ONPREM]


class ArkDPAVMPoliciesEditorService(
    ArkDPABasePoliciesEditorService[ArkDPAVMPolicy, ArkDPAVMPolicyListItem, ArkDPAVMAddPolicy, ArkDPAVMUpdatePolicy, ArkDPAVMGeneratePolicy]
):
    def __init__(self, isp_auth: ArkISPAuth, policies_cache_dir: Optional[str] = None, profile: Optional[ArkProfile] = None) -> None:
        self.__policies_service: ArkDPAVMPoliciesService = ArkDPAVMPoliciesService(isp_auth)
        super().__init__(
            ArkDPAVMPolicy,
            ArkDPAVMAddPolicy,
            ArkDPAVMUpdatePolicy,
            isp_auth,
            'vm',
            self.__policies_service.isp_client.tenant_id,
            policies_cache_dir,
            profile,
        )

    @overrides
    def _policy(self, get_policy: ArkDPAGetPolicy) -> ArkDPAVMPolicy:
        return self.__policies_service.policy(get_policy)

    @overrides
    def _list_policies(self) -> List[ArkDPAVMPolicyListItem]:
        return self.__policies_service.list_policies()

    @overrides
    def _add_policy(self, add_policy: ArkDPAVMAddPolicy) -> ArkDPAVMPolicy:
        return self.__policies_service.add_policy(add_policy)

    @overrides
    def _update_policy(self, update_policy: ArkDPAVMUpdatePolicy) -> ArkDPAVMPolicy:
        return self.__policies_service.update_policy(update_policy)

    @overrides
    def _delete_policy(self, delete_policy: ArkDPADeletePolicy) -> None:
        self.__policies_service.delete_policy(delete_policy)

    @overrides
    def _generate_policy(self, generate_policy: ArkDPAVMGeneratePolicy, workspace_policies: List[ArkDPAVMPolicy]) -> ArkDPAVMPolicy:
        inquires = []
        if not generate_policy.name:
            inquires.append(inquirer.Text('name', 'Please supply a policy name'))
        if not generate_policy.providers:
            inquires.append(
                inquirer.Checkbox(
                    'providers',
                    'Please select the providers for the policy (can be omitted and later edited)',
                    choices=['AWS', 'Azure', 'GCP', 'OnPrem'],
                )
            )
        if not generate_policy.protocols:
            inquires.append(
                inquirer.Checkbox(
                    'protocols', 'Please select the protocols for the policy (can be omitted and later edited)', choices=['ssh', 'rdp']
                )
            )
        if inquires:
            answers = inquirer.prompt(inquires, render=ArkInquirerRender())
            if not answers:
                return
            generate_policy.name = answers['name']
            generate_policy.providers = answers['providers']
            generate_policy.protocols = answers['protocols']
        if not generate_policy.name:
            generate_policy.name = 'Default VM Policy'
        while generate_policy.name in workspace_policies:
            answers = inquirer.prompt(
                [inquirer.Text('name', f'Policy name {generate_policy.name} already exists, please write a different one')],
                render=ArkInquirerRender(),
            )
            if not answers:
                return
            generate_policy.name = answers['name'] or generate_policy.name
        policy: ArkDPAVMPolicy = DEFAULT_GENERATED_POLICY.copy()
        if generate_policy.name:
            policy.policy_name = generate_policy.name
        rule = DEFAULT_GENERATED_AUTHORIZATION_RULE.copy()
        if generate_policy.providers:
            for provider in generate_policy.providers:
                if ArkWorkspaceType(provider) in DEFAULT_GENERATED_PROVIDERS:
                    policy.providers_data[provider] = DEFAULT_GENERATED_PROVIDERS[ArkWorkspaceType(provider)].copy()
        if generate_policy.protocols:
            if ArkProtocolType.SSH in generate_policy.protocols:
                for provider in generate_policy.providers:
                    # Supported SSH protocol providers
                    if ArkWorkspaceType(provider) in SUPPORTED_SSH_PROTOCOL_PROVIDERS:
                        rule.connection_information.connect_as[provider] = {
                            ArkProtocolType.SSH: DEFAULT_GENERATED_PROTOCOLS[ArkProtocolType.SSH]
                        }
            if ArkProtocolType.RDP in generate_policy.protocols:
                for provider in generate_policy.providers:
                    # Supported RDP protocol providers
                    if ArkWorkspaceType(provider) in SUPPORTED_RDP_PROTOCOL_PROVIDERS:
                        if provider not in rule.connection_information.connect_as:
                            rule.connection_information.connect_as[provider] = {}
                        rule.connection_information.connect_as[provider][ArkProtocolType.RDP] = DEFAULT_GENERATED_PROTOCOLS[
                            ArkProtocolType.RDP
                        ]
        policy.user_access_rules.append(rule)
        return policy

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
