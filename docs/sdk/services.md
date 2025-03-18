---
title: Services
description: Services
---

# Services

SDK services are defined to execute requests on available ISP services (such as SIA). When a service is initialized, a valid authenticator is required to authorize access to the ISP service. To perform service actions, each service exposes a set of classes and methods.

Here's an example that initializes the `ArkSIADBPoliciesService` service:

```python
import pprint

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret, IdentityArkAuthMethodSettings
from ark_sdk_python.services.sia.policies import ArkSIAPoliciesService

if __name__ == '__main__':
    isp_auth = ArkISPAuth(cache_authentication=False)
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username='tina@cyberark.cloud.12345',
            auth_method=ArkAuthMethod.Identity,
            auth_method_settings=IdentityArkAuthMethodSettings(),
        ),
        secret=ArkSecret(secret="CoolPassword"),
    )
    policies_service = ArkSIADBPoliciesService(isp_auth=isp_auth)
    policies = policies_service.list_policies()
    for policy in policies:
        pprint.pprint(policy.json(indent=4))
```

The above example authenticates to the specified ISP tenant, initializes a SIA policies service using the authorized authenticator, and then uses the service to list the policies.

## Dynamic Privilege Access service

The Dynamic Privilege Access (SIA) service requires the ArkISPAuth authenticator, and exposes these service classes:

- <b>ArkSIACertificatesService (certificates)</b> - SIA certificates service
- <b>ArkSIASSOService (sso)</b> - SIA end-user SSO service
- <b>ArkSIAK8SService (kubernetes)</b> - SIA end-user Kubernetes service
- <b>ArkSIADatabasesService (databases)</b> - SIA end-user databases service
- <b>ArkSIAPoliciesService (policies)</b> - SIA policies management
    - <b>ArkSIADBPoliciesService (db)</b> - SIA DB policies management
        - **ArkSIADBPoliciesEditorService (editor)** - SIA DB policies interactive
    - <b>ArkSIAVMPoliciesService (vm)</b> - SIA VM policies management
        - **ArkSIAVMPoliciesEditorService (editor)** - SIA VM policies interactive
- <b>ArkSIASecretsService (secrets)</b> - SIA secrets management
    - <b>ArkSIADBSecretsService (db)</b> - SIA DB secrets services
    - <b>ArkSIAVMSecretsService (vm)</b> - SIA VM secrets services
- <b>ArkSIAWorkspacesService (workspaces)</b> - SIA workspaces management
    - <b>ArkSIADBWorkspaceService (db)</b> - SIA DB workspace management
    - <b>ArkSIATargetSetsWorkspaceService (db)</b> - SIA Target Sets workspace management


## Session monitoring service
The Session Monitoring (SM) service requires ArkISPAuth authenticator, and exposes these service classes:
- <b>ArkSMService (sm)</b> - Session Monitoring Service


## Identity service
The Identity (identity) service requires ArkISPAuth authenticator, and exposes those service classes:
- <b>ArkIdentityRolesService - Identity roles service
- <b>ArkIdentityUsersService - Identity users service
- <b>ArkIdentityPoliciesService - Identity policies service
- <b>ArkIdentityDirectoriesService - Identity directories service


## Privilege Cloud service
The Privilege Cloud (pcloud) service requires ArkISPAuth authenticator, and exposes those service classes:
- <b>ArkPCloudAccountsService</b> - Accounts management service
- <b>ArkPCloudSafesService</b> - Safes management service
- <b>ArkPCloudPlatformsService</b> - Platforms management service
