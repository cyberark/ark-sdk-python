---
title: Simple SDK workflow
description: Simple SDK Workflow
---

# Simple SDK workflow

This example shows how to create, with a Python script, a demo environment that contains the required SIA DB assets:

```python
ArkSystemConfig.disable_verbose_logging()
# Authenticate to the tenant with an auth profile to configure SIA
print(f'Authenticating to the created tenant with user [{username}]')
isp_auth = ArkISPAuth()
isp_auth.authenticate(auth_profile=ArkAuthProfile(
    username='user@cyberark.cloud.12345',
    auth_method=ArkAuthMethod.Identity,
    auth_method_settings=IdentityArkAuthMethodSettings()
), secret=ArkSecret(secret='CoolPassword'))

# Create SIA DB secret, database, connector, and DB policy
sia_service = ArkSIAAPI(isp_auth)
print('Adding SIA DB User Secret')
secret = sia_service.secrets_db.add_secret(ArkSIADBAddSecret(
    secret_type=ArkSIADBSecretType.UsernamePassword,
    username='Administrator',
    password='CoolPassword'
))
print('Adding SIA Database')
sia_service.workspace_db.add_database(ArkSIADBAddDatabase(
    name='mydomain.com',
    provider_engine=ArkSIADBDatabaseEngineType.PosgresSH,
    secret_id=secret.secret_id,
    read_write_endpoint="myendpoint.mydomain.com"
))
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
```

In the script above, the following actions are defined:

- The admin user is logged in to perform actions on the tenant (lines 4-9)
- The SIA's secret, database, and policy are configured (lines 12-65)
