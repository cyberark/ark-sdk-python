---
title: Working With Profiles
description: Working With Profiles
---

# Working With Profiles
Profiles are the way to work with the CLI (and the SDK, but less dominant)

As such, each profile can be configured seperatly via ark configure command

Each subsequent command can receive --profile-name to work with the specific configured profile

Alongside that, ARK_PROFILE environment variable can be set to globally work with a profile instead of passing it as a parameter all the times

All of the profiles are json files that reside on $HOME/.ark_profiles folder

A profile looks as follows:

```json
{
    "profile_name": "ark",
    "profile_description": "Default Ark Profile",
    "auth_profiles": {
        "isp": {
            "username": "tina@cyberark.cloud.1234567",
            "auth_method": "identity",
            "auth_method_settings": {
                "identity_mfa_method": "email",
                "identity_mfa_interactive": true,
                "identity_application": null,
                "identity_url": null
            }
        }
    }
}
```

Profiles can be added / removed via the configure command, or manipulating the profiles folder