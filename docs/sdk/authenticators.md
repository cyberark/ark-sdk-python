---
title: Authenticators
description: Authenticators
---

# Authenticators

## Motivation
An authenticator provides the abilities to authenticate to a cyberark resource based on authentication profiles, where an authentication profile contains the auth method to authenticate with, along with settings that are coupled to the authentication method

An example of creating an authenticator can be seen as follows:

```python
from ark_sdk_python.auth import ArkISPAuth

auth = ArkISPAuth(cache_authentication=False)
```

Notice that each authenticator can cache its authenticated credentials if need be, and we can disable it on the constructor

Each authentictor has a base authenticate method, which receives a auth profile or a profile as an input and outputs / saves a token

Alongside that, each authenticator class exposes what the auth methods that are authenticator supports

The token can be used as a return value or can be ignored as it is also saved internally

There are different types of authenticators and auth methods implemented:

## Auth methods
- <b>Identity (identity)</b> - Identity authentication, to a tenant or to an application within the identity tenant, used in conjunction with IdentityArkAuthMethodSettings
- <b>IdentityServiceUser (identity_service_user)</b> - Same idea as identity, but with a service user, used in conjunction with IdentityServiceUserArkAuthMethodSettings
- <b>Direct (direct)</b> - Direct authentication to an endpoint, used in conjunction with DirectArkAuthMethodSettings
- <b>default</b> - Default authenticator auth method for the authenticator
- <b>other </b>- Custom implemented

More on the auth methods can be seen on [ark_auth_method.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/auth/ark_auth_method.py){:target="_blank" rel="noopener"}


## Authenticator Types
- <b>ArkISPAuth (isp)</b> - Authenticator to a specific tenant in the platform
    - Auth Methods: identity, identity_service_user
    - Default: identity

## Authenticating in the SDK
When u wish to authenticate to a resource, an example authentication flow would look as follows:

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
dpa_api = ArkDPAAPI(isp_auth=isp_auth)
```

Where in the above example, we create an authenticator, and authenticate to a specific ISP tenant, using identity authentication type with a given username and password

Once authenticated, the authenticate method can return a token but it can also be ignored if not needed as it is stored internally.

The authenticator can be passed on to the fitting service for the service execution.
