---
title: Refresh authentication
description: Refreshing Authentication
---

# Refresh authentication

When you want to continue working with an existing authenticator, you can refresh the authentications. You can refresh authentications for the following:

- The login command
- The exec command
- Polling operations
- Via the SDK code

## Login command

To try to authenticate with an existing authenticator, use the `-ra `or `--refresh-auth` CLI flag:
```bash  linenums="0"
ark login -ra
```
The `-ra` flag indicates that the user's profile authenticator should be refreshed and used for authentication. The user is only prompted for additional authentication values when the refresh fails.

## Exec command

To try to run any command with an existing authenticator, use the `-ra `or -`-refresh-auth` CLI flag:
```bash  linenums="0"
ark exec -ra dpa policies list-policies
```

The `-ra` flag indicates that the user's profile authenticator should be refreshed and used before executing the command. When the refresh fails, an error is returned and you must log in again.

## Polling operations

When polling any async command, a timeout can occur before the polling operation finishes. To try and overcome these timeouts, you can enable automatic authentication refreshes for polling operations.

When refreshed are configured, if an unauthorized (`401`) response is returned, Ark refreshes the authenticator before the next poll. When the refresh fails, a timeout error is reported in the CLI. 

To enable refreshes, use the `-parc` or `--poll-allow-refresh-connection` CLI flag.

## SDK

When using the SDK, use the `load_authentication` method to attempt using a cached authenticator (with a refresh if required):
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
