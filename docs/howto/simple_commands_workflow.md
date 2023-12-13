---
title: Simple Commands Workflow
description: Simple Commands Workflow
---

# Simple Commands Workflow

Let's configure a profile to login to that respective tenant and perform DPA actions om:

```shell
ark configure --work-with-isp --isp-username=username
ark login -s --isp-secret=secret
```

Actions such as configuring a database, secret and generating a policy can be done as follows:

```shell
ark exec dpa secrets db add-secret -sn name -st username_password -u user -pa coolpassword
ark exec dpa workspaces db add-database -n somedb -pe postgres-sh -rwe myendpoint.domain.com
ark exec dpa policies db editor generate-policy
```
