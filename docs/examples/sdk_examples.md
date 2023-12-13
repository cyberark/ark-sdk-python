---
title: SDK Examples
description: SDK Examples
---

# SDK Examples
Using the SDK is similar to using the CLI

## Read tenant db policies
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