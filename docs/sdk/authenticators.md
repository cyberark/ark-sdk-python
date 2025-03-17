---
title: Authenticators
description: Authenticators
---

# Authenticators

An authenticator provides the ability to authenticate to a CyberArk Identity Security Platform (ISP) resource. The authentication is based on authentication profiles, where the authentication profile defines the authentication method and its associated settings.

Here's an example of initialize an authenticator:

```python
from ark_sdk_python.auth import ArkISPAuth

auth = ArkISPAuth(cache_authentication=False)
```

!!! note
    When you call the constructor, you can determine whether or not the authentication credentials are cached.

The Authenticators have a base authenticate method that receives a profile as an input and returns an auth token. Additionally, the ArkISPAuth class exposes functions to retrieve a profile's authentication methods and settings. Although the returned token can be used as a return value, it can normally be ignored as it is saved internally.

These are the different types of authenticator types and auth methods:

## Authenticator types

Currently, ArkISPAuth is the only supported authenticator type, which is derived from the ArkISPAuth class and accepts the `Identity` (default) and `IdentityServiceUser` auth methods.

## Auth methods

- <b>Identity</b> (`identity`) - Identity authentication to a tenant or to an application within the Identity tenant, used with the IdentityArkAuthMethodSettings class
- <b>IdentityServiceUser</b> (`identity_service_user`) - Identity authentication with a service user, used with IdentityServiceUserArkAuthMethodSettings class
- <b>Direct</b> (`direct`) - Direct authentication to an endpoint, used with the DirectArkAuthMethodSettings class
- <b>Default</b> (`default`) - Default authenticator auth method for the authenticator
- <b>Other</b> (`other`) - For custom implementations

See [ark_auth_method.py](https://github.com/cyberark/ark-sdk-python/blob/main/ark_sdk_python/models/auth/ark_auth_method.py){:target="_blank" rel="noopener"} for more information about auth methods.

## SDK authenticate example

Here is an example authentication flow that uses implements the ArkISPAuth class:

```python
from ark_sdk_python.auth import ArkISPAuth

isp_auth = ArkISPAuth(cache_authentication=False)
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username='smarom@cyberark.cloud.84573',
        auth_method=ArkAuthMethod.Identity,
        auth_method_settings=IdentityArkAuthMethodSettings(),
    ),
    secret=ArkSecret(secret="CoolPassword"),
)
sia_api = ArkSIAAPI(isp_auth=isp_auth)
```

The example above initializes an instance of the ArkISPAuth class and authenticates to the specified ISP tenant, using the `Identity` authentication type with the provided username and password.

The `authenticate` method returns a token, which be ignored because it is stored internally.

After authenticating, the authenticator can be used passed to the services you want to access.
