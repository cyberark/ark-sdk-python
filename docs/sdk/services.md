---
title: Services
description: Services
---

# Services

SDK services are defined to execute requests on available ISP services (such as DPA). When a service is initialized, a valid authenticator is required to authorize access to the ISP service. To perform service actions, each service exposes a set of classes and methods.

Here's an example that initializes the `ArkDPADBPoliciesService` service:

```python
import pprint

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret, IdentityArkAuthMethodSettings
from ark_sdk_python.services.dpa.policies import ArkDPAPoliciesService

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
    policies_service = ArkDPADBPoliciesService(isp_auth=isp_auth)
    policies = policies_service.list_policies()
    for policy in policies:
        pprint.pprint(policy.json(indent=4))
```

The above example authenticates to the specified ISP tenant, initializes a DPA policies service using the authorized authenticator, and then uses the service to list the policies.

## Dynamic Privilege Access service

The Dynamic Privilege Access (DPA) service requires the ArkISPAuth authenticator, and exposes these service classes:

- <b>ArkDPACertificatesService (certificates)</b> - DPA certificates service
- <b>ArkDPASSOService (sso)</b> - DPA end-user SSO service
- <b>ArkDPAK8SService (kubernetes)</b> - DPA end-user Kubernetes service
- <b>ArkDPADatabasesService (databases)</b> - DPA end-user databases service
- <b>ArkDPAPoliciesService (policies)</b> - DPA policies management
    - <b>ArkDPADBPoliciesService (db)</b> - DPA DB policies management
        - **ArkDPADBPoliciesEditorService (editor)** - DPA DB policies interactive
    - <b>ArkDPAVMPoliciesService (vm)</b> - DPA VM policies management
        - **ArkDPAVMPoliciesEditorService (editor)** - DPA VM policies interactive
- <b>ArkDPASecretsService (secrets)</b> - DPA secrets management
    - <b>ArkDPADBSecretsService (db)</b> - DPA DB secrets services
- <b>ArkDPAWorkspacesService (workspaces)</b> - DPA workspaces management
    - <b>ArkDPADBWorkspaceService (db)</b> - DPA DB workspace management


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
