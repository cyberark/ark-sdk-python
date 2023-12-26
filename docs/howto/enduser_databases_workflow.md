---
title: Enduser Databases Workflow
description: Enduser Databases Workflow
---

# Enduser Databases Workflow
Say an end user wants to connect to a database
to do so, he would perform the following steps:

First, he would install ark-sdk-python using pip if he did not do so already

Afterwards, he would configure a profile once as follows interactivaly:
```shell
ark configure
```
Or silently:
```shell
ark configure --silent --work-with-isp --isp-username myuser
```

Now that we configured a profile, we may log into it
```shell
ark login --silent --isp-secret mysecret
```

Now that the user is logged in, he may execute actions, one of them being generating a short lived sso password
```shell
ark exec dpa sso short-lived-password
```

The user will receive a secret which he can use to connect to his database of choice, for example postgres
```shell
psql "host=mytenant.postgres.cyberark.cloud user=user@cyberark.cloud.12345@postgres@mypostgres.fqdn.com"
```

Or, using ark
```shell
ark exec dpa db psql --target-username postgres --target-address mypostgres.fqdn.com
```