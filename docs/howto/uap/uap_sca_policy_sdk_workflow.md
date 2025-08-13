---
title: UAP SCA policy SDK workflow
description: Creating a UAP SCA Policy using Ark SDK
---

# UAP SCA policy SDK workflow
Here is an example workflow for adding a UAP SCA policy assets via the SDK:

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

# Create UAP SCA Policy
uap_sca_service = ArkUAPSIASCAService(isp_auth)

print('Adding UAP SCA Policy')
uap_sca_service.add_policy(ArkUAPSIASCAAccessPolicy(
        metadata=ArkUAPMetadata(
            name='Cool Policy',
            description='Cool Policy Description',
            status=ArkUAPPolicyStatus(status=ArkUAPStatusType.ACTIVE),
            time_frame=ArkUAPTimeFrame(from_time=None, to_time=None),
            policy_entitlement=ArkUAPPolicyEntitlement(
                target_category=ArkCategoryType.CLOUD_CONSOLE,
                location_type=ArkWorkspaceType.AWS,
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
        targets=ArkUAPSCACloudConsoleTarget(aws_account_targets=[
            ArkUAPSCAAWSAccountTarget(
                role_id='arn:aws:iam::123456789012:role/ExampleRole',
                workspace_id='123456789012',
                role_name='ExampleRole',
                workspace_name='ExampleWorkspace',
            ),
        ])
    )
)
print('Finished Successfully')
```

In the script above, the following actions are defined:

- The admin user is logged in to perform actions on the tenant
- we then configure UAP SCA policy
