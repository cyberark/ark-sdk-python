---
title: SDK examples
description: SDK Examples
---

# SDK examples

This page lists some useful SDK examples.

## Authenticate and read tenant DB policies

```python
from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.auth import ArkSecret, ArkAuthMethod, ArkAuthProfile, IdentityArkAuthMethodSettings
from ark_sdk_python.services.dpa.policies.db import ArkDPADBPoliciesService

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username='tina@cyberark.cloud.12345', auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
        ),
        secret=ArkSecret(secret='CoolPassword'),
    )
    db_policies_service = ArkDPADBPoliciesService(isp_auth)
    policies = db_policies_service.list_policies()
```

## Authenticate and provision DPA databases and policy

```python
if __name__ == '__main__':
    ArkSystemConfig.disable_verbose_logging()
    # Authenticate to the tenant with an auth profile to configure DPA
    username = 'user@cyberark.cloud.12345'
    print(f'Authenticating to the created tenant with user [{username}]')
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
        ),
        secret=ArkSecret(secret='CoolPassword'),
    )

    # Create DPA DB Secret, Database, Connector and DB Policy
    dpa_service = ArkDPAAPI(isp_auth)
    print('Adding DPA DB User Secret')
    secret = dpa_service.secrets_db.add_secret(
        ArkDPADBAddSecret(secret_type=ArkDPADBSecretType.UsernamePassword, username='Administrator', password='CoolPassword')
    )
    print('Adding DPA Database')
    dpa_service.workspace_db.add_database(
        ArkDPADBAddDatabase(
            name='mydomain.com',
            provider_engine=ArkDPADBDatabaseEngineType.PostgresSH,
            secret_id=secret.secret_id,
            read_write_endpoint="myendpoint.mydomain.com",
        )
    )
    print('Adding DPA DB Policy')
    dpa_service.policies_db.add_policy(
        ArkDPADBAddPolicy(
            policy_name='IT Policy',
            status=ArkDPARuleStatus.Active,
            description='IT Policy',
            providers_data=ArkDPADBProvidersData(
                postgres=ArkDPADBPostgres(
                    resources=['postgres-onboarded-asset'],
                ),
            ),
            user_access_rules=[
                ArkDPADBAuthorizationRule(
                    rule_name='IT Rule',
                    user_data=ArkDPAUserData(roles=['DpaAdmin'], groups=[], users=[]),
                    connection_information=ArkDPADBConnectionInformation(
                        grant_access=2,
                        idle_time=10,
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
            ],
        )
    )
```

## Authenticate and provision DPA VM policies

```python
isp_auth = ArkISPAuth()
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
    ),
    secret=ArkSecret(secret='CoolPassword'),
)
print('Adding DPA Policy')
dpa_service.policies.add_policy(
    ArkDPAVMAddPolicy(
        policy_name='IT Policy',
        description='IT Policy',
        status=ArkDPARuleStatus.Enabled,
        providers_data={
            ArkWorkspaceType.AWS: ArkDPAVMAWSProviderData(
                account_ids=['965428623928'], tags=[{'key': 'team', 'value': 'IT'}], regions=[], vpc_ids=[]
            )
        },
        user_access_rules=[
            ArkDPAVMAuthorizationRule(
                rule_name='IT Rule',
                user_data=ArkDPAUserData(roles=['IT']),
                connection_information=ArkDPAVMConnectionInformation(
                    full_days=True,
                    days_of_week=[],
                    time_zone='Asia/Jerusalem',
                    connect_as={
                        ArkWorkspaceType.AWS: {
                            ArkProtocolType.SSH: 'root',
                            ArkProtocolType.RDP: ArkDPAVMRDPLocalEphemeralUserConnectionData(
                                local_ephemeral_user=ArkDPAVMLocalEphemeralUserConnectionMethodData(assign_groups={'Administrators'})
                            ),
                        }
                    },
                ),
            )
        ],
    )
)
```

## View Session Monitoring Sessions And Activities Per Session

```python
from ark_sdk_python.services.sm import ArkSMService
from ark_sdk_python.models.services.sm import ArkSMSessionsFilter, ArkSMGetSession, ArkSMGetSessionActivities
from ark_sdk_python.models.ark_profile import ArkProfileLoader
from ark_sdk_python.models.common import ArkProtocolType
from ark_sdk_python.auth import ArkISPAuth
from datetime import datetime, timedelta

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(
        profile=ArkProfileLoader().load_default_profile()
    )
    sm: ArkSMService = ArkSMService(isp_auth)
    search_by = 'startTime ge {start_time_from} AND sessionDuration GE {min_duration} AND protocol IN {protocols}'
    search_by = search_by.format(
        start_time_from=(datetime.utcnow() - timedelta(days=30)).isoformat(timespec='seconds'),
        min_duration='00:00:01',
        protocols=','.join([ArkProtocolType.DB[0], ArkProtocolType.SSH[0], ArkProtocolType.RDP[0]]),
    )
    sessions_filter = ArkSMSessionsFilter(
        search=search_by,
    )
    print(f'session_count = {sm.count_sessions_by(sessions_filter)}')
    for s_page in sm.list_sessions_by(sessions_filter):
        for session in s_page.items:
            session = sm.session(ArkSMGetSession(session_id=session.session_id))
            get_session_activities = ArkSMGetSessionActivities(session_id=session.session_id)
            print(f'session = {session}, activities_count = {sm.count_session_activities(get_session_activities)}')
            session_activities = [activity for page in sm.list_session_activities(get_session_activities) for activity in page.items]
            print(session_activities)
```

## Get current tenant default suffix

```python
from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.ark_profile import ArkProfileLoader
from ark_sdk_python.models.services.identity.directories import ArkIdentityListDirectoriesEntities
from ark_sdk_python.services.identity import ArkIdentityAPI

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(ArkProfileLoader().load_default_profile())
    identity_api = ArkIdentityAPI(isp_auth)
    print(identity_api.identity_directories.tenant_default_suffix())
    for page in identity_api.identity_directories.list_directories_entities(ArkIdentityListDirectoriesEntities()):
        print([i.name for i in page.items])
```


## Add identity role and user

```python
from ark_sdk_python.models.auth import (
    ArkAuthMethod,
    ArkAuthProfile,
    ArkSecret,
    IdentityArkAuthMethodSettings,
)
from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.services.identity import ArkIdentityAPI
from ark_sdk_python.models.services.identity.roles import ArkIdentityCreateRole
from ark_sdk_python.models.services.identity.users import ArkIdentityCreateUser

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username='CoolUser', auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
        ),
        secret=ArkSecret(secret='CoolPassword'),
    )

    # Create an identity service to create some users and roles
    print('Creating identity roles and users')
    identity_api = ArkIdentityAPI(isp_auth)
    identity_api.identity_roles.create_role(ArkIdentityCreateRole(role_name='IT'))
    identity_api.identity_users.create_user(ArkIdentityCreateUser(username='it_user', password='CoolPassword', roles=['IT']))
```
