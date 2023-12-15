---
title: Getting Started
description: Getting started
---

# Getting Started

## Installation

One can install the SDK via the community pypi with the following command:
```shell
pip3 install ark-sdk-python
```

## CLI Usage

Both the SDK and the CLI works with profiles

The profiles can be configured upon need and be used for the consecutive actions

The CLI has the following basic commands:

- <b>configure</b> - Configures profiles and their respective authentication methods
- <b>login</b> - Logs into the profile authentication methods
- <b>exec</b> - Executes different commands based on the supported services
- <b>profiles</b> - Manage multiple profiles on the machine
- <b>cache</b> - Manage ark cache on the machine


## TL;DR - Basic flow

A basic flow for an end user would look something as follows

The user, after installing ark-sdk, would first configure a profile, interactively or silently

```shell
ark configure --silent --work-with-isp --isp-username myuser
```

Once configured, he can login
```shell
ark login --silent --isp-secret mysecret
```

Now that the user is logged in, he may execute actions, one of them being generating a short lived sso password
```shell
ark exec dpa sso short-lived-password
```
