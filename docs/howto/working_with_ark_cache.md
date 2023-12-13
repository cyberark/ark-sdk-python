---
title: Working With Ark Cache
description: Working With Ark Cache
---

# Working With Ark Cache
Both the CLI and the SDK work cache of the machine or a fallback encrypted folder located in $HOME/.ark_cache

The cache is used to store login information in an encrypted manner, that can be used later on for execution of commands until the authentication tokens are expired or invalid

Machines such as windows support keyrings inside the windows certificate store and linux support keyring on the machine

Other machines may fallback if not supported to an encrypted folder on the system

The cache keyring folder can be set via the ARK_KEYRING_FOLDER env var, and the ark sdk can be forced to only work with the filesystem using the ARK_BASIC_KEYRING environment variable

When performing the ark login operation, one can force the login to ignore the cache like this:
```bash
ark login -f
```

Alongside that, caching can be disabled in the SDK for authenticators like this:
```python
isp_auth = ArkISPAuth(cache_authentication=False)
```

Lastly, cache can be completely cleared by simply removing it from the filesystem under $HOME/.ark_cache