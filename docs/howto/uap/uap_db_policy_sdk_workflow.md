---
title: UAP database policy SDK workflow
description: Creating a UAP DB Policy using Ark SDK
---

# UAP database policy SDK workflow
Here is an example workflow for adding a UAP DB policy alongside all needed assets via the SDK:

```python
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

# Create SIA DB Secret, Database, Connector and UAP DB Policy
uap_db_service = ArkUAPSIADBService(isp_auth)
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
print('Adding UAP DB Policy')
uap_db_service.add_policy(
    ArkUAPSIADBAccessPolicy(
        metadata=ArkUAPMetadata(
            name='Cool Policy',
            description='Cool Policy Description',
            status=ArkUAPPolicyStatus(status=ArkUAPStatusType.ACTIVE),
            time_frame=ArkUAPTimeFrame(from_time=None, to_time=None),
            policy_entitlement=ArkUAPPolicyEntitlement(
                target_category=ArkCategoryType.DB,
                location_type=ArkWorkspaceType.FQDN_IP,
                policy_type=ArkUAPPolicyType.RECURRING),
            created_by=ArkUAPChangeInfo(user='cool_user', time=datetime.datetime(2025, 2, 8, 22, 46, 6)),
            updated_on=ArkUAPChangeInfo(user='cool_user', time=datetime.datetime(2025, 2, 8, 22, 46, 6)),
            policy_tags=['cool_tag', 'cool_tag2'],
            time_zone='Asia/Jerusalem'),
        principals=[ArkUAPPrincipal(
            id='principal_id',
            name='tester@cyberark.cloud',
            source_directory_name='CyberArk Cloud Directory',
            source_directory_id='source_directory_id',
            type=ArkUAPPrincipalType.USER)],
        conditions=ArkUAPSIACommonConditions(
            access_window=ArkUAPTimeCondition(
                days_of_the_week=[0, 1, 2, 3, 4, 5, 6],
                from_hour='05:00',
                to_hour='23:59'),
            max_session_duration=2,
            idle_time=1),
        targets={
            ArkWorkspaceType.FQDN_IP: ArkUAPSIADBTargets(
                instances=[
                    ArkUAPSIADBInstanceTarget(
                        instance_name='Mongo-atlas_ephemeral_user',
                        instance_type=ArkSIADBDatabaseFamilyType.Mongo,
                        instance_id='1234',
                        authentication_method=ArkUAPSIADBAuthenticationMethod.MONGO_AUTH,
                        profile=ArkUAPSIADBMongoAuthProfile(
                            global_builtin_roles=[ArkSIADBMongoGlobalBuiltinRole.ReadWriteAnyDatabase],
                            database_builtin_roles={'mydb1': [ArkSIADBMongoDatabaseBuiltinRole.UserAdmin],
                                                    'mydb2': [ArkSIADBMongoDatabaseBuiltinRole.DbAdmin]},
                            database_custom_roles={'mydb1': ['myCoolRole']}
                        )
                    )
                ]
            )
        }
    )
)
print('Finished Successfully')
```

In the script above, the following actions are defined:

- The admin user is logged in to perform actions on the tenant
- we then configure SIA's secret, database and UAP DB policy
