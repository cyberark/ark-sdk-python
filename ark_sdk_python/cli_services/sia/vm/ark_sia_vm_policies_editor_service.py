from datetime import date, timedelta
from typing import Dict, Final, List, Optional

import inquirer
from overrides import overrides

from ark_sdk_python.args.ark_args_formatter import ArkInquirerRender
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.cli_services.sia.common.ark_sia_base_policies_editor_service import ArkSIABasePoliciesEditorService
from ark_sdk_python.models.ark_profile import ArkProfile
from ark_sdk_python.models.cli_services.sia.policies_editor.vm import ArkSIAVMGeneratePolicy
from ark_sdk_python.models.common import ArkProtocolType, ArkWorkspaceType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.policies.common import (
    ArkSIADeletePolicy,
    ArkSIAGetPolicy,
    ArkSIARuleStatus,
    ArkSIAUserData,
    ArkSIAUserDataAttribute,
)
from ark_sdk_python.models.services.sia.policies.vm import (
    ArkSIAVMAddPolicy,
    ArkSIAVMAuthorizationRule,
    ArkSIAVMAWSProviderData,
    ArkSIAVMAzureProviderData,
    ArkSIAVMConnectionDataType,
    ArkSIAVMConnectionInformation,
    ArkSIAVMFQDNOperator,
    ArkSIAVMFQDNRule,
    ArkSIAVMGCPProviderData,
    ArkSIAVMLocalEphemeralUserConnectionMethodData,
    ArkSIAVMOnPremProviderData,
    ArkSIAVMPolicy,
    ArkSIAVMPolicyListItem,
    ArkSIAVMProvider,
    ArkSIAVMRDPLocalEphemeralUserConnectionData,
    ArkSIAVMUpdatePolicy,
)
from ark_sdk_python.services.sia.policies.vm.ark_sia_vm_policies_service import ArkSIAVMPoliciesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-policies-vm-editor', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
DEFAULT_GENERATED_POLICY: Final[ArkSIAVMPolicy] = ArkSIAVMPolicy(
    policy_name='Default VM Policy',
    status=ArkSIARuleStatus.Draft,
    description='Auto generated vm policy',
    providers_data={},
    start_date=date.today().strftime('%Y-%m-%d'),
    end_date=(date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
    user_access_rules=[],
)
DEFAULT_GENERATED_AUTHORIZATION_RULE: Final[ArkSIAVMAuthorizationRule] = ArkSIAVMAuthorizationRule(
    rule_name='Default VM Rule',
    user_data=ArkSIAUserData(roles=[ArkSIAUserDataAttribute(name='DpaAdmin')], groups=[], users=[]),
    connection_information=ArkSIAVMConnectionInformation(
        connect_as={},
        grant_access=2,
        idle_time=10,
        days_of_week=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        full_days=False,
        hours_from='07:00',
        hours_to='17:00',
        time_zone='Asia/Jerusalem',
    ),
)
DEFAULT_GENERATED_PROVIDERS: Final[Dict[ArkWorkspaceType, ArkSIAVMProvider]] = {
    ArkWorkspaceType.AWS: ArkSIAVMAWSProviderData(regions=[], tags=[{'key': 'value'}], vpc_ids=[], account_ids=[]),
    ArkWorkspaceType.AZURE: ArkSIAVMAzureProviderData(
        azure_regions=[], azure_tags=[{'key': 'value'}], azure_resource_groups=[], azure_vnet_ids=[], azure_subscriptions=[]
    ),
    ArkWorkspaceType.GCP: ArkSIAVMGCPProviderData(regions=[], tags=[{'key': 'value'}], network_ids=[], projects=[]),
    ArkWorkspaceType.ONPREM: ArkSIAVMOnPremProviderData(
        fqdn_rules=[ArkSIAVMFQDNRule(operator=ArkSIAVMFQDNOperator.WILDCARD, computername_pattern='*', domain='default.com')],
    ),
}
DEFAULT_GENERATED_PROTOCOLS: Final[Dict[ArkProtocolType, ArkSIAVMConnectionDataType]] = {
    ArkProtocolType.SSH: 'root',
    ArkProtocolType.RDP: ArkSIAVMRDPLocalEphemeralUserConnectionData(
        local_ephemeral_user=ArkSIAVMLocalEphemeralUserConnectionMethodData(assign_groups={'Administrators'})
    ),
}
SUPPORTED_SSH_PROTOCOL_PROVIDERS: Final[ArkWorkspaceType] = [
    ArkWorkspaceType.AWS,
    ArkWorkspaceType.AZURE,
    ArkWorkspaceType.GCP,
    ArkWorkspaceType.ONPREM,
]
SUPPORTED_RDP_PROTOCOL_PROVIDERS: Final[ArkWorkspaceType] = [
    ArkWorkspaceType.AWS,
    ArkWorkspaceType.AZURE,
    ArkWorkspaceType.GCP,
    ArkWorkspaceType.ONPREM,
]


class ArkSIAVMPoliciesEditorService(
    ArkSIABasePoliciesEditorService[ArkSIAVMPolicy, ArkSIAVMPolicyListItem, ArkSIAVMAddPolicy, ArkSIAVMUpdatePolicy, ArkSIAVMGeneratePolicy]
):
    def __init__(self, isp_auth: ArkISPAuth, policies_cache_dir: Optional[str] = None, profile: Optional[ArkProfile] = None) -> None:
        self.__policies_service: ArkSIAVMPoliciesService = ArkSIAVMPoliciesService(isp_auth)
        super().__init__(
            ArkSIAVMPolicy,
            ArkSIAVMAddPolicy,
            ArkSIAVMUpdatePolicy,
            isp_auth,
            'vm',
            self.__policies_service.isp_client.tenant_id,
            policies_cache_dir,
            profile,
        )

    @overrides
    def _policy(self, get_policy: ArkSIAGetPolicy) -> ArkSIAVMPolicy:
        return self.__policies_service.policy(get_policy)

    @overrides
    def _list_policies(self) -> List[ArkSIAVMPolicyListItem]:
        return self.__policies_service.list_policies()

    @overrides
    def _add_policy(self, add_policy: ArkSIAVMAddPolicy) -> ArkSIAVMPolicy:
        return self.__policies_service.add_policy(add_policy)

    @overrides
    def _update_policy(self, update_policy: ArkSIAVMUpdatePolicy) -> ArkSIAVMPolicy:
        return self.__policies_service.update_policy(update_policy)

    @overrides
    def _delete_policy(self, delete_policy: ArkSIADeletePolicy) -> None:
        self.__policies_service.delete_policy(delete_policy)

    @overrides
    def _generate_policy(self, generate_policy: ArkSIAVMGeneratePolicy, workspace_policies: List[ArkSIAVMPolicy]) -> ArkSIAVMPolicy:
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
        policy: ArkSIAVMPolicy = DEFAULT_GENERATED_POLICY.model_copy()
        if generate_policy.name:
            policy.policy_name = generate_policy.name
        rule = DEFAULT_GENERATED_AUTHORIZATION_RULE.model_copy()
        if generate_policy.providers:
            for provider in generate_policy.providers:
                if ArkWorkspaceType(provider) in DEFAULT_GENERATED_PROVIDERS:
                    policy.providers_data[provider] = DEFAULT_GENERATED_PROVIDERS[ArkWorkspaceType(provider)].model_copy()
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
                        # pylint: disable-next=no-member
                        if provider not in rule.connection_information.connect_as:
                            # pylint: disable-next=no-member
                            rule.connection_information.connect_as[provider] = {}
                        # pylint: disable-next=no-member
                        rule.connection_information.connect_as[provider][ArkProtocolType.RDP] = DEFAULT_GENERATED_PROTOCOLS[
                            ArkProtocolType.RDP
                        ]
        # pylint: disable-next=no-member
        policy.user_access_rules.append(rule)
        return policy

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
