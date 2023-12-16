---
title: Services
description: Services
---

# Services

## Motivation
A service is whats executing the actual requests, in a context of the authenticators that were created with it

Each service exposes a set of API's specifically to the service, and receives in its constructor a set of authenticators to work with

A service exposes its service_config, containing which authenticators are required and which are optional for the service to work

A service usage can be seen as follows:

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

Where in the above example, we authenticate to a specific ISP tenant, and create a DPA policies service, and then use it to list the policies

Each service only needs to expose its service_config in order to be supported in the SDK

## Services
There are alot of different supported functions, the following is a list of supported services and their authenticators

- <b>Dynamic Privilege Access Services</b>
    - <b>ArkDPACertificatesService (certificates)</b> - DPA Certificates service
        - Required Authenticators: isp
        - Optional Authenticators: None
    - <b>ArkDPASSOService (sso)</b> - DPA Enduser SSO service
        - Required Authenticators: isp
        - Optional Authenticators: None
    - <b>ArkDPAK8SService (kubernetes)</b> - DPA Enduser Kubernetes service
        - Required Authenticators: isp
        - Optional Authenticators: None
    - <b>ArkDPADatabasesService (databases)</b> - DPA Endusr Databases service
        - Required Authenticators: isp
        - Optional Authenticators: None
    - <b>ArkDPAPoliciesService (policies)</b> - DPA Policies Management
        - <b>ArkDPADBPoliciesService (db)</b> - DPA DB Policies Management
            - ArkDPADBPoliciesEditorService (editor) - DPA DB Policies Interactive
            - Required Authenticators: isp
            - Optional Authenticators: None
        - <b>ArkDPAVMPoliciesService (vm)</b> - DPA VM Policies Management
            - ArkDPAVMPoliciesEditorService (editor) - DPA VM Policies Interactive
            - Required Authenticators: isp
            - Optional Authenticators: None
    - <b>ArkDPASecretsService (secrets)</b> - DPA Secrets Management
        - <b>ArkDPADBSecretsService (db)</b> - DPA DB Secrets Services
            - Required Authenticators: isp
            - Optional Authenticators: None
    - <b>ArkDPAWorkspacesService (workspaces)</b> - DPA Workspaces Management
        - Required Authenticators: isp
        - Optional Authenticators: None
        - <b>ArkDPADBWorkspaceService (db)</b> - DPA DB Workspace Management
            - Required Authenticators: isp
            - Optional Authenticators: None
