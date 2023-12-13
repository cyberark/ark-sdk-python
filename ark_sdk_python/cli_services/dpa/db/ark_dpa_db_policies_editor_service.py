from datetime import date, timedelta
from typing import Dict, Final, List, Optional

import inquirer
from overrides import overrides

from ark_sdk_python.args.ark_args_formatter import ArkInquirerRender
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.cli_services.dpa.common.ark_dpa_base_policies_editor_service import ArkDPABasePoliciesEditorService
from ark_sdk_python.models.ark_profile import ArkProfile
from ark_sdk_python.models.cli_services.dpa.policies_editor.db import ArkDPADBGeneratePolicy
from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.policies.common import ArkDPADeletePolicy, ArkDPAGetPolicy, ArkDPARuleStatus, ArkDPAUserData
from ark_sdk_python.models.services.dpa.policies.db import (
    ArkDPADB,
    ArkDPADBAddPolicy,
    ArkDPADBAppliedTo,
    ArkDPADBAuthorizationRule,
    ArkDPADBBaseAuth,
    ArkDPADBConnectAs,
    ArkDPADBConnectionInformation,
    ArkDPADBLDAPAuth,
    ArkDPADBLocalDBAuth,
    ArkDPADBMariaDB,
    ArkDPADBMSSQL,
    ArkDPADBMySQL,
    ArkDPADBOracle,
    ArkDPADBOracleDBAuth,
    ArkDPADBOracleResource,
    ArkDPADBPolicy,
    ArkDPADBPolicyListItem,
    ArkDPADBPostgres,
    ArkDPADBProvidersData,
    ArkDPADBResourceIdentifierType,
    ArkDPADBUpdatePolicy,
)
from ark_sdk_python.services.dpa.policies.db.ark_dpa_db_policies_service import ArkDPADBPoliciesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-policies-db-editor', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
SUPPORTED_DATABASE_TYPES: Final[List[str]] = [
    'MSSQL',
    'MySQL',
    'MariaDB',
    'Postgres',
    'Oracle',
]
DEFAULT_GENERATED_POLICY: Final[ArkDPADBPolicy] = ArkDPADBPolicy(
    policy_name='Default DB Policy',
    status=ArkDPARuleStatus.Draft,
    description='Auto generated db policy',
    providers_data=ArkDPADBProvidersData(
        postgres=ArkDPADBPostgres(
            resources=['postgres-onboarded-asset'],
        ),
    ),
    start_date=date.today().strftime('%Y-%m-%d'),
    end_date=(date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
    user_access_rules=[],
)
DEFAULT_GENERATED_PROVIDERS: Final[Dict[ArkWorkspaceType, ArkDPADB]] = {
    ArkWorkspaceType.MSSQL: ArkDPADBMSSQL(resources=['mssql-onboarded-asset']),
    ArkWorkspaceType.MYSQL: ArkDPADBMySQL(resources=['mysql-onboarded-asset']),
    ArkWorkspaceType.MARIADB: ArkDPADBMariaDB(resources=['mariadb-onboarded-asset']),
    ArkWorkspaceType.POSTGRES: ArkDPADBPostgres(resources=['postgres-onboarded-asset']),
    ArkWorkspaceType.ORACLE: ArkDPADBOracle(
        resources=[
            ArkDPADBOracleResource(
                name='oracle-onboarded-asset',
                services=['XE'],
            ),
        ],
    ),
}
DEFAULT_GENERATED_AUTH_METHODS: Final[Dict[ArkWorkspaceType, ArkDPADBBaseAuth]] = {
    ArkWorkspaceType.MSSQL: ArkDPADBLDAPAuth(
        assign_groups=['DomainSQLAdmins'],
        applied_to=[
            ArkDPADBAppliedTo(
                name='mssql-onboarded-asset',
                type=ArkDPADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.MYSQL: ArkDPADBLocalDBAuth(
        roles=['db_admin'],
        applied_to=[
            ArkDPADBAppliedTo(
                name='mysql-onboarded-asset',
                type=ArkDPADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.MARIADB: ArkDPADBLocalDBAuth(
        roles=['db_admin'],
        applied_to=[
            ArkDPADBAppliedTo(
                name='mariadb-onboarded-asset',
                type=ArkDPADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.POSTGRES: ArkDPADBLocalDBAuth(
        roles=['rds_superuser'],
        applied_to=[
            ArkDPADBAppliedTo(
                name='postgres-onboarded-asset',
                type=ArkDPADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.ORACLE: ArkDPADBOracleDBAuth(
        roles=[],
        dba_role=True,
        sysdba_role=True,
        sysoper_role=False,
        applied_to=[
            ArkDPADBAppliedTo(
                name='oracle-onboarded-asset',
                type=ArkDPADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
}
DEFAULT_GENERATED_AUTHORIZATION_RULE: Final[ArkDPADBAuthorizationRule] = ArkDPADBAuthorizationRule(
    rule_name='Default DB Rule',
    user_data=ArkDPAUserData(roles=['DpaAdmin'], groups=[], users=[]),
    connection_information=ArkDPADBConnectionInformation(
        grant_access=2,
        idle_time=10,
        days_of_week=[],
        full_days=True,
        hours_from='07:00',
        hours_to='17:00',
        time_zone='Asia/Jerusalem',
        connect_as=ArkDPADBConnectAs(
            db_auth=[
                ArkDPADBLocalDBAuth(
                    roles=['rds_superuser'],
                    applied_to=[
                        ArkDPADBAppliedTo(
                            name='postgres-onboarded-asset',
                            type=ArkDPADBResourceIdentifierType.RESOURCE,
                        )
                    ],
                ),
            ],
        ),
    ),
)
WORKSPACE_TO_PROVIDER_NAME: Final[Dict[ArkWorkspaceType, str]] = {
    ArkWorkspaceType.MSSQL: 'mssql',
    ArkWorkspaceType.MYSQL: 'mysql',
    ArkWorkspaceType.POSTGRES: 'postgres',
    ArkWorkspaceType.ORACLE: 'oracle',
    ArkWorkspaceType.MARIADB: 'mariadb',
}


class ArkDPADBPoliciesEditorService(
    ArkDPABasePoliciesEditorService[ArkDPADBPolicy, ArkDPADBPolicyListItem, ArkDPADBAddPolicy, ArkDPADBUpdatePolicy, ArkDPADBGeneratePolicy]
):
    def __init__(self, isp_auth: ArkISPAuth, policies_cache_dir: Optional[str] = None, profile: Optional[ArkProfile] = None) -> None:
        self.__policies_service: ArkDPADBPoliciesService = ArkDPADBPoliciesService(isp_auth)
        super().__init__(
            ArkDPADBPolicy,
            ArkDPADBAddPolicy,
            ArkDPADBUpdatePolicy,
            isp_auth,
            'db',
            self.__policies_service.isp_client.tenant_id,
            policies_cache_dir,
            profile,
        )

    @overrides
    def _policy(self, get_policy: ArkDPAGetPolicy) -> ArkDPADBPolicy:
        return self.__policies_service.policy(get_policy)

    @overrides
    def _list_policies(self) -> List[ArkDPADBPolicyListItem]:
        return self.__policies_service.list_policies()

    @overrides
    def _add_policy(self, add_policy: ArkDPADBAddPolicy) -> ArkDPADBPolicy:
        return self.__policies_service.add_policy(add_policy)

    @overrides
    def _update_policy(self, update_policy: ArkDPADBUpdatePolicy) -> ArkDPADBPolicy:
        return self.__policies_service.update_policy(update_policy)

    @overrides
    def _delete_policy(self, delete_policy: ArkDPADeletePolicy) -> None:
        self.__policies_service.delete_policy(delete_policy)

    @overrides
    def _generate_policy(self, generate_policy: ArkDPADBGeneratePolicy, workspace_policies: List[ArkDPADBPolicy]) -> ArkDPADBPolicy:
        inquires = []
        if not generate_policy.name:
            inquires.append(inquirer.Text('name', 'Please supply a policy name'))
        if not generate_policy.providers:
            inquires.append(
                inquirer.Checkbox(
                    'providers',
                    'Please select the database providers for the policy (can be omitted and later edited)',
                    choices=SUPPORTED_DATABASE_TYPES,
                )
            )
        if inquires:
            answers = inquirer.prompt(inquires, render=ArkInquirerRender())
            if not answers:
                return
            generate_policy.name = answers['name']
            generate_policy.providers = answers['providers']
        if not generate_policy.name:
            generate_policy.name = 'Default DB Policy'
        while generate_policy.name in workspace_policies:
            answers = inquirer.prompt(
                [inquirer.Text('name', f'Policy name {generate_policy.name} already exists, please write a different one')],
                render=ArkInquirerRender(),
            )
            if not answers:
                return
            generate_policy.name = answers['name'] or generate_policy.name
        policy: ArkDPADBPolicy = DEFAULT_GENERATED_POLICY.copy()
        if generate_policy.name:
            policy.policy_name = generate_policy.name
        rule = DEFAULT_GENERATED_AUTHORIZATION_RULE.copy()
        if generate_policy.providers:
            generated_providers = {}
            generated_auth_methods = {}
            for provider in generate_policy.providers:
                if ArkWorkspaceType(provider) in DEFAULT_GENERATED_PROVIDERS:
                    generated_providers[WORKSPACE_TO_PROVIDER_NAME[ArkWorkspaceType(provider)]] = DEFAULT_GENERATED_PROVIDERS[
                        ArkWorkspaceType(provider)
                    ].copy()
                if ArkWorkspaceType(provider) in DEFAULT_GENERATED_AUTH_METHODS:
                    if isinstance(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)], ArkDPADBLocalDBAuth):
                        if 'db_auth' not in generated_auth_methods:
                            generated_auth_methods['db_auth'] = []
                        generated_auth_methods['db_auth'].append(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)])
                    if isinstance(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)], ArkDPADBLDAPAuth):
                        if 'ldap_auth' not in generated_auth_methods:
                            generated_auth_methods['ldap_auth'] = []
                        generated_auth_methods['ldap_auth'].append(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)])
                    if isinstance(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)], ArkDPADBOracleDBAuth):
                        if 'oracle_auth' not in generated_auth_methods:
                            generated_auth_methods['oracle_auth'] = []
                        generated_auth_methods['oracle_auth'].append(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)])
            policy.providers_data = ArkDPADBProvidersData(**generated_providers)
            rule.connection_information.connect_as = ArkDPADBConnectAs(**generated_auth_methods)
        policy.user_access_rules.append(rule)
        return policy

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
