---
title: Simple commands workflow
description: Simple commands workflow
---

# Simple commands workflow

Here's an example of how to:

1. Configure a profile for logging in to a tenant
1. Log in to the tenant
1. Run a SIA action to configure a database secret and policy


## Configure profile and log in
```shell
ark configure --work-with-isp --isp-username=username
ark login -s --isp-secret=secret
```

## Configure a database secret and policy
```shell
ark exec sia secrets db add-secret -sn name -st username_password -u user -pa coolpassword
ark exec sia workspaces db add-database -n somedb -pe postgres-sh -rwe myendpoint.domain.com
ark exec sia policies db editor generate-policy
```
