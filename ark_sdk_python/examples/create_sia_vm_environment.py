from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.common import ArkSystemConfig
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret, IdentityArkAuthMethodSettings
from ark_sdk_python.models.common import ArkOsType, ArkProtocolType, ArkWorkspaceType
from ark_sdk_python.models.services.sia.access import ArkSIAInstallConnector
from ark_sdk_python.models.services.sia.policies.common import ArkSIARuleStatus, ArkSIAUserData
from ark_sdk_python.models.services.sia.policies.vm import ArkSIAVMAddPolicy
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_authorization_rule import (
    ArkSIAVMAuthorizationRule,
    ArkSIAVMConnectionInformation,
)
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_connection_data import (
    ArkSIAVMLocalEphemeralUserConnectionMethodData,
    ArkSIAVMRDPLocalEphemeralUserConnectionData,
)
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_providers import (
    ArkSIAVMFQDNOperator,
    ArkSIAVMFQDNRule,
    ArkSIAVMOnPremProviderData,
)
from ark_sdk_python.models.services.sia.secrets.vm import ArkSIAVMAddSecret, ArkSIAVMSecretType
from ark_sdk_python.models.services.sia.workspaces.targetsets import ArkSIAAddTargetSet
from ark_sdk_python.services.sia import ArkSIAAPI

if __name__ == '__main__':
    ArkSystemConfig.disable_verbose_logging()
    # Authenticate to the tenant with an auth profile to configure SIA
    username = 'user@cyberark.cloud.12345'
    print(f'Authenticating to the created tenant with user [{username}]')
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
        ),
        secret=ArkSecret(secret='CoolPassword'),
    )

    # Create SIA VM Secret, Target Set and VM Policy
    sia_service = ArkSIAAPI(isp_auth)
    print('Adding SIA VM User Secret')
    secret = sia_service.secrets_vm.add_secret(
        ArkSIAVMAddSecret(
            secret_type=ArkSIAVMSecretType.ProvisionerUser,
            provisioner_username='Administrator',
            provisioner_password='CoolPassword',
        ),
    )
    print('Adding SIA Target Set')
    sia_service.workspace_target_sets.add_target_set(
        ArkSIAAddTargetSet(
            name='mydomain.com',
            secret_type=ArkSIAVMSecretType.ProvisionerUser,
            secret_id=secret.secret_id,
        )
    )
    print('Installing SIA Connector')
    sia_service.access.install_connector(
        ArkSIAInstallConnector(
            connector_os=ArkOsType.LINUX,
            connector_type=ArkWorkspaceType.ONPREM,
            connector_pool_id='pool_id',
            target_machine='1.2.3.4',
            username='root',
            private_key_path='/path/to/private.pem',
        )
    )
    print('Adding SIA VM Policy')
    sia_service.policies_vm.add_policy(
        ArkSIAVMAddPolicy(
            policy_name='IT Policy',
            status=ArkSIARuleStatus.Enabled,
            description='IT Policy',
            providers_data={
                ArkWorkspaceType.ONPREM: ArkSIAVMOnPremProviderData(
                    fqdn_rules=[
                        ArkSIAVMFQDNRule(
                            operator=ArkSIAVMFQDNOperator.WILDCARD,
                            computername_pattern='*',
                            domain='mydomain.com',
                        ),
                    ],
                ),
            },
            user_access_rules=[
                ArkSIAVMAuthorizationRule(
                    rule_name='IT Rule',
                    user_data=ArkSIAUserData(roles=['DpaAdmin'], groups=[], users=[]),
                    connection_information=ArkSIAVMConnectionInformation(
                        grant_access=2,
                        idle_time=10,
                        full_days=True,
                        hours_from='07:00',
                        hours_to='17:00',
                        time_zone='Asia/Jerusalem',
                        connect_as={
                            ArkWorkspaceType.ONPREM: {
                                ArkProtocolType.RDP: ArkSIAVMRDPLocalEphemeralUserConnectionData(
                                    local_ephemeral_user=ArkSIAVMLocalEphemeralUserConnectionMethodData(
                                        assign_groups=['Administrators'],
                                    ),
                                ),
                            },
                        },
                    ),
                )
            ],
        )
    )
    print('Finished Successfully')
