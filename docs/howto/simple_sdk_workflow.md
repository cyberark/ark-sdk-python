---
title: Simple SDK Workflow
description: Simple SDK Workflow
---

# Simple SDK Workflow
Let's say we want to create a demo environment containing all needed DPA DB assets

To do so, we can use the following script:

```python
ArkSystemConfig.disable_verbose_logging()
# Authenticate to the tenant with an auth profile to configure DPA
print(f'Authenticating to the created tenant with user [{username}]')
isp_auth = ArkISPAuth()
isp_auth.authenticate(auth_profile=ArkAuthProfile(
    username='user@cyberark.cloud.12345',
    auth_method=ArkAuthMethod.Identity,
    auth_method_settings=IdentityArkAuthMethodSettings()
), secret=ArkSecret(secret='CoolPassword'))

# Create DPA DB Secret, Database, Connector and DB Policy
dpa_service = ArkDPAAPI(isp_auth)
print('Adding DPA DB User Secret')
secret = dpa_service.secrets_db.add_secret(ArkDPADBAddSecret(
    secret_type=ArkDPADBSecretType.UsernamePassword,
    username='Administrator',
    password='CoolPassword'
))
print('Adding DPA Database')
dpa_service.workspace_db.add_database(ArkDPADBAddDatabase(
    name='mydomain.com',
    provider_engine=ArkDPADBDatabaseEngineType.PosgresSH,
    secret_id=secret.secret_id,
    read_write_endpoint="myendpoint.mydomain.com"
))
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
print('Finished Successfully')
```

Where in the above the following flow occurres:
- We login to the admin user in order to perform actions on the tenant
- we then configure DPA's secret, database and policy
