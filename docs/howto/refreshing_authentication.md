---
title: Refreshing Authentication
description: Refreshing Authentication
---

# Refreshing Authentication
In cases where we would like to continue working directly with existing authentications, we can perform a refresh to the existing authentication that we have

The refresh authentication is possible in the following 4 use cases:
- The login command
- The exec command
- During polling operation
- Via the SDK when working with it

## Login
When we would like to login to our authenticators, but instead of writing our passwords again, or any other tokens, but only to refresh the existing login if possible and the refresh time has not expired as well, we can perform the following command for example with the CLI paran -ra / --refresh-auth:

```bash
ark login -ra
```

The above command will try and refresh the authentication of the existing profile, and if it has failed, it will fallback to the normal authentication and ask the user for fitting details

## Exec
When we would like to execute a command, if any kind, we can try and refresh the authentication before running the command, This will cause it so the Ark CLI will perform refresh to the authenticator if possible and if it has failed, an exception will be thrown. This can be used as follows for example with the CLI paran -ra / --refresh-auth

```bash
ark exec -ra dpa policies list-policies
```

# Polling Operations
When polling, on any async command, we might hit a timeout before the polling operation has ended. to compensate that, we can add an automatic refresh during the polling operation, this will make it so that if an unauthorized (401) response of different polling operations arrives, we will try to refresh the fitting authentication before continuing to poll
If it has failed, will report it as a timeout error in the CLI. This can be used as follows for example with the CLI param -parc / --poll-allow-refresh-connection

# SDK
In the SDK, this is similar to the CLI, where we can call an existing authenticator "load_authentication" command
This will try if caching is enabled to load auth from cache, and if given, also try and refresh the authentication either from the loaded cache or from the existing auth in memory, as seen in the following example:

```python
isp_auth = ArkISPAuth()
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
    ),
    secret=ArkSecret(secret='CoolPassword'),
)
...
isp_auth.load_authentication(refresh_auth=True)
```

Or if we are talking about polling operation, we can use poll_allow_refreshable_connection arg

```python
isp_auth = ArkISPAuth()
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
    ),
    secret=ArkSecret(secret='CoolPassword'),
)
dpa_service = ArkDPAAPI(isp_auth)
...
```
