from datetime import date, timedelta
from typing import Dict, Final, List, Optional

import inquirer
from overrides import overrides

from ark_sdk_python.args.ark_args_formatter import ArkInquirerRender
from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.cli_services.sia.common.ark_sia_base_policies_editor_service import ArkSIABasePoliciesEditorService
from ark_sdk_python.models.ark_profile import ArkProfile
from ark_sdk_python.models.cli_services.sia.policies_editor.db import ArkSIADBGeneratePolicy
from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sia.policies.common import ArkSIADeletePolicy, ArkSIAGetPolicy, ArkSIARuleStatus, ArkSIAUserData
from ark_sdk_python.models.services.sia.policies.db import (
    ArkSIADB,
    ArkSIADBAddPolicy,
    ArkSIADBAppliedTo,
    ArkSIADBAuthorizationRule,
    ArkSIADBBaseAuth,
    ArkSIADBConnectAs,
    ArkSIADBConnectionInformation,
    ArkSIADBDb2,
    ArkSIADBLDAPAuth,
    ArkSIADBLocalDBAuth,
    ArkSIADBMariaDB,
    ArkSIADBMongo,
    ArkSIADBMongoDBAuth,
    ArkSIADBMongoGlobalBuiltinRole,
    ArkSIADBMSSQL,
    ArkSIADBMySQL,
    ArkSIADBOracle,
    ArkSIADBOracleDBAuth,
    ArkSIADBOracleResource,
    ArkSIADBPolicy,
    ArkSIADBPolicyListItem,
    ArkSIADBPostgres,
    ArkSIADBProvidersData,
    ArkSIADBResourceIdentifierType,
    ArkSIADBUpdatePolicy,
)
from ark_sdk_python.services.sia.policies.db.ark_sia_db_policies_service import ArkSIADBPoliciesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sia-policies-db-editor', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
SUPPORTED_DATABASE_TYPES: Final[List[str]] = [
    'MSSQL',
    'MySQL',
    'MariaDB',
    'Postgres',
    'Oracle',
    'DB2',
    'Mongo',
]
DEFAULT_GENERATED_POLICY: Final[ArkSIADBPolicy] = ArkSIADBPolicy(
    policy_name='Default DB Policy',
    status=ArkSIARuleStatus.Draft,
    description='Auto generated db policy',
    providers_data=ArkSIADBProvidersData(
        postgres=ArkSIADBPostgres(
            resources=['postgres-onboarded-asset'],
        ),
    ),
    start_date=date.today().strftime('%Y-%m-%d'),
    end_date=(date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
    user_access_rules=[],
)
DEFAULT_GENERATED_PROVIDERS: Final[Dict[ArkWorkspaceType, ArkSIADB]] = {
    ArkWorkspaceType.MSSQL: ArkSIADBMSSQL(resources=['mssql-onboarded-asset']),
    ArkWorkspaceType.MYSQL: ArkSIADBMySQL(resources=['mysql-onboarded-asset']),
    ArkWorkspaceType.MARIADB: ArkSIADBMariaDB(resources=['mariadb-onboarded-asset']),
    ArkWorkspaceType.POSTGRES: ArkSIADBPostgres(resources=['postgres-onboarded-asset']),
    ArkWorkspaceType.ORACLE: ArkSIADBOracle(
        resources=[
            ArkSIADBOracleResource(
                name='oracle-onboarded-asset',
                services=['XE'],
            ),
        ],
    ),
    ArkWorkspaceType.DB2: ArkSIADBDb2(resources=['db2-onboarded-asset']),
    ArkWorkspaceType.MONGO: ArkSIADBMongo(resources=['mongo-onboarded-asset']),
}
DEFAULT_GENERATED_AUTH_METHODS: Final[Dict[ArkWorkspaceType, ArkSIADBBaseAuth]] = {
    ArkWorkspaceType.MSSQL: ArkSIADBLDAPAuth(
        assign_groups=['DomainSQLAdmins'],
        applied_to=[
            ArkSIADBAppliedTo(
                name='mssql-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.MYSQL: ArkSIADBLocalDBAuth(
        roles=['db_admin'],
        applied_to=[
            ArkSIADBAppliedTo(
                name='mysql-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.MARIADB: ArkSIADBLocalDBAuth(
        roles=['db_admin'],
        applied_to=[
            ArkSIADBAppliedTo(
                name='mariadb-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.POSTGRES: ArkSIADBLocalDBAuth(
        roles=['rds_superuser'],
        applied_to=[
            ArkSIADBAppliedTo(
                name='postgres-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.ORACLE: ArkSIADBOracleDBAuth(
        roles=[],
        dba_role=True,
        sysdba_role=True,
        sysoper_role=False,
        applied_to=[
            ArkSIADBAppliedTo(
                name='oracle-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.DB2: ArkSIADBLDAPAuth(
        assign_groups=['DomainSQLAdmins'],
        applied_to=[
            ArkSIADBAppliedTo(
                name='db2-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            )
        ],
    ),
    ArkWorkspaceType.MONGO: ArkSIADBMongoDBAuth(
        global_builtin_roles=[
            ArkSIADBMongoGlobalBuiltinRole.DbAdminAnyDatabase,
        ],
        applied_to=[
            ArkSIADBAppliedTo(
                name='mongo-onboarded-asset',
                type=ArkSIADBResourceIdentifierType.RESOURCE,
            ),
        ],
    ),
}
DEFAULT_GENERATED_AUTHORIZATION_RULE: Final[ArkSIADBAuthorizationRule] = ArkSIADBAuthorizationRule(
    rule_name='Default DB Rule',
    user_data=ArkSIAUserData(roles=['DpaAdmin'], groups=[], users=[]),
    connection_information=ArkSIADBConnectionInformation(
        grant_access=2,
        idle_time=10,
        days_of_week=[],
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
WORKSPACE_TO_PROVIDER_NAME: Final[Dict[ArkWorkspaceType, str]] = {
    ArkWorkspaceType.MSSQL: 'mssql',
    ArkWorkspaceType.MYSQL: 'mysql',
    ArkWorkspaceType.POSTGRES: 'postgres',
    ArkWorkspaceType.ORACLE: 'oracle',
    ArkWorkspaceType.MARIADB: 'mariadb',
    ArkWorkspaceType.DB2: 'db2',
    ArkWorkspaceType.MONGO: 'mongo',
}


class ArkSIADBPoliciesEditorService(
    ArkSIABasePoliciesEditorService[ArkSIADBPolicy, ArkSIADBPolicyListItem, ArkSIADBAddPolicy, ArkSIADBUpdatePolicy, ArkSIADBGeneratePolicy]
):
    def __init__(self, isp_auth: ArkISPAuth, policies_cache_dir: Optional[str] = None, profile: Optional[ArkProfile] = None) -> None:
        self.__policies_service: ArkSIADBPoliciesService = ArkSIADBPoliciesService(isp_auth)
        super().__init__(
            ArkSIADBPolicy,
            ArkSIADBAddPolicy,
            ArkSIADBUpdatePolicy,
            isp_auth,
            'db',
            self.__policies_service.isp_client.tenant_id,
            policies_cache_dir,
            profile,
        )

    @overrides
    def _policy(self, get_policy: ArkSIAGetPolicy) -> ArkSIADBPolicy:
        return self.__policies_service.policy(get_policy)

    @overrides
    def _list_policies(self) -> List[ArkSIADBPolicyListItem]:
        return self.__policies_service.list_policies()

    @overrides
    def _add_policy(self, add_policy: ArkSIADBAddPolicy) -> ArkSIADBPolicy:
        return self.__policies_service.add_policy(add_policy)

    @overrides
    def _update_policy(self, update_policy: ArkSIADBUpdatePolicy) -> ArkSIADBPolicy:
        return self.__policies_service.update_policy(update_policy)

    @overrides
    def _delete_policy(self, delete_policy: ArkSIADeletePolicy) -> None:
        self.__policies_service.delete_policy(delete_policy)

    @overrides
    def _generate_policy(self, generate_policy: ArkSIADBGeneratePolicy, workspace_policies: List[ArkSIADBPolicy]) -> ArkSIADBPolicy:
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
        policy: ArkSIADBPolicy = DEFAULT_GENERATED_POLICY.model_copy()
        if generate_policy.name:
            policy.policy_name = generate_policy.name
        rule = DEFAULT_GENERATED_AUTHORIZATION_RULE.model_copy()
        if generate_policy.providers:
            generated_providers = {}
            generated_auth_methods = {}
            for provider in generate_policy.providers:
                if ArkWorkspaceType(provider) in DEFAULT_GENERATED_PROVIDERS:
                    generated_providers[WORKSPACE_TO_PROVIDER_NAME[ArkWorkspaceType(provider)]] = DEFAULT_GENERATED_PROVIDERS[
                        ArkWorkspaceType(provider)
                    ].model_copy()
                if ArkWorkspaceType(provider) in DEFAULT_GENERATED_AUTH_METHODS:
                    if isinstance(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)], ArkSIADBLocalDBAuth):
                        if 'db_auth' not in generated_auth_methods:
                            generated_auth_methods['db_auth'] = []
                        generated_auth_methods['db_auth'].append(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)])
                    if isinstance(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)], ArkSIADBLDAPAuth):
                        if 'ldap_auth' not in generated_auth_methods:
                            generated_auth_methods['ldap_auth'] = []
                        generated_auth_methods['ldap_auth'].append(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)])
                    if isinstance(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)], ArkSIADBOracleDBAuth):
                        if 'oracle_auth' not in generated_auth_methods:
                            generated_auth_methods['oracle_auth'] = []
                        generated_auth_methods['oracle_auth'].append(DEFAULT_GENERATED_AUTH_METHODS[ArkWorkspaceType(provider)])
            policy.providers_data = ArkSIADBProvidersData(**generated_providers)
            rule.connection_information.connect_as = ArkSIADBConnectAs(**generated_auth_methods)
        # pylint: disable-next=no-member
        policy.user_access_rules.append(rule)
        return policy

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
