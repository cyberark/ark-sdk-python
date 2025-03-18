from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.common import ArkSystemConfig
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret, IdentityArkAuthMethodSettings
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType
from ark_sdk_python.models.services.sia.access import ArkSIAInstallConnector
from ark_sdk_python.models.services.sia.policies.common import ArkSIARuleStatus, ArkSIAUserData
from ark_sdk_python.models.services.sia.policies.db import (
    ArkSIADBAddPolicy,
    ArkSIADBAppliedTo,
    ArkSIADBAuthorizationRule,
    ArkSIADBConnectAs,
    ArkSIADBConnectionInformation,
    ArkSIADBLocalDBAuth,
    ArkSIADBPostgres,
    ArkSIADBProvidersData,
    ArkSIADBResourceIdentifierType,
)
from ark_sdk_python.models.services.sia.secrets.db import ArkSIADBAddSecret, ArkSIADBSecretType
from ark_sdk_python.models.services.sia.workspaces.db import ArkSIADBAddDatabase, ArkSIADBDatabaseEngineType
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

    # Create SIA DB Secret, Database and DB Policy
    sia_service = ArkSIAAPI(isp_auth)
    print('Adding SIA DB User Secret')
    secret = sia_service.secrets_db.add_secret(
        ArkSIADBAddSecret(secret_type=ArkSIADBSecretType.UsernamePassword, username='Administrator', password='CoolPassword')
    )
    print('Adding SIA Database')
    sia_service.workspace_db.add_database(
        ArkSIADBAddDatabase(
            name='mydomain.com',
            provider_engine=ArkSIADBDatabaseEngineType.PostgresSH,
            secret_id=secret.secret_id,
            read_write_endpoint="myendpoint.mydomain.com",
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
    print('Adding SIA DB Policy')
    sia_service.policies_db.add_policy(
        ArkSIADBAddPolicy(
            policy_name='IT Policy',
            status=ArkSIARuleStatus.Enabled,
            description='IT Policy',
            providers_data=ArkSIADBProvidersData(
                postgres=ArkSIADBPostgres(
                    resources=['postgres-onboarded-asset'],
                ),
            ),
            user_access_rules=[
                ArkSIADBAuthorizationRule(
                    rule_name='IT Rule',
                    user_data=ArkSIAUserData(roles=['DpaAdmin'], groups=[], users=[]),
                    connection_information=ArkSIADBConnectionInformation(
                        grant_access=2,
                        idle_time=10,
                        full_days=True,
                        hours_from='07:00',
                        hours_to='17:00',
                        time_zone='Asia/Jerusalem',
                        connect_as=ArkSIADBConnectAs(
                            db_auth=[
                                ArkSIADBLocalDBAuth(
                                    roles=['rds_superuser'],
                                    applied_to=[
                                        ArkSIADBAppliedTo(
                                            name='postgres-onboarded-asset',
                                            type=ArkSIADBResourceIdentifierType.RESOURCE,
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ),
                )
            ],
        )
    )
    print('Finished Successfully')
