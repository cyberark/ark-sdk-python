---
title: Getting started
description: Getting started
---

# Getting started

## Installation

You can install the SDK via [PyPI](https://pypi.org/) with the following command:
```shell linenums="0"
pip3 install ark-sdk-python
```

You may also upgrade the SDK via [PyPI](https://pypi.org/) to the latest version with the following command:
```shell linenums="0"
pip3 install -U ark-sdk-python
```

## CLI Usage

Both the SDK and the CLI support [profiles](howto/working_with_profiles.md), which can be configured as needed and used for consecutive actions.

The CLI has the following basic commands:

- <b>configure</b>: Configure profiles and their authentication methods (see [Configure](commands/configure.md))
- <b>login</b>: Log in using the configured profile authentication methods (see [Login](commands/login.md))
- <b>exec</b>: Execute commands for supported services (see [Exec](commands/exec.md))
- <b>profiles</b>: Manage multiple profiles on the machine (see [Profiles](commands/profiles.md))
- <b>cache</b>: Manage ark cache on the machine (see [Cache](commands/cache.md))


### Basic flow

1. Install Ark SDK and then configure a profile (either silently or interactively):  
    ``` shell linenums="0"
    ark configure --silent --work-with-isp --isp-username myuser
    ```

1. After the profile is configured, log in:
    ``` shell linenums="0"
    ark login --silent --isp-secret mysecret
    ```

1. Execute actions (such as generating a short-lived SSO password):
    ``` shell linenums="0"
    ark exec dpa sso short-lived-password
    ```
