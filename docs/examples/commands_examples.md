---
title: Commands examples
description: Commands Examples
---

# Commands examples

This page lists some useful CLI examples.

!!! note

    You can disable certificate validation for login to an authenticator using the `--disable-certificate-verification` flag. **This option is not recommended.**

    **Useful environment variables**

    - `ARK_PROFILE`: Sets the profile to be used across the CLI
    - `ARK_DISABLE_CERTIFICATE_VERIFICATION`: Disables certificate verification for REST APIs

## Configure command example

The `configure` command works in interactive or silent mode. When using silent mode, the required parameters need to specified. Here's an example of configuring ISP in silent mode:

```bash linenums="0"
ark configure --profile-name="PROD" --work-with-isp --isp-username="tina@cyberark.cloud.12345" --silent --allow-output
```

## Login commands Example

The login command can work in interactive or silent mode. Here's an example of a silent login with the profile configured in the example above:
```bash linenums="0"
ark login -s --isp-secret=CoolPasswordß
```

## Exec command examples

Use the `--help` flag to view all `exec` options.

### Add DPA database secret

```shell linenums="0"
ark exec dpa secrets db add-secret --secret-name mysecret --secret-type username_password --username user --password mypass
```

### Delete DPA database secret

```shell linenums="0"
ark exec dpa secrets db delete-secret --secret-name mysecret
```

### Add DPA database

```shell linenums="0"
ark exec dpa workspaces db add-database --name mydb --provider-engine postgres-sh --read-write-endpoint myendpoint.domain.com
```

### List DPA databases

```shell linenums="0"
ark exec dpa workspaces db list-databases
```

### Get VM policies stats

```shell linenums="0"
ark exec dpa policies vm policies-stats
```

### Edit policies interactively example

This example shows how to locally work with a policies workspace, and edit, reset, and create policies that are applied to both databases and VM policies. After the local policies are ready, you can commit all the policies changes to the remote workspace.

To load and reload policies locally:

```shell linenums="0"
ark exec dpa policies vm editor load-policies
```

After loading the policies, use these commands to edit them:
```shell
ark exec dpa policies vm editor edit-policies
ark exec dpa policies vm editor view-policies
ark exec dpa policies vm editor reset-policies
ark exec dpa policies vm editor generate-policy
ark exec dpa policies vm editor remove-policies
ark exec dpa policies vm editor policies diff
```

When they are ready to be committed, run:
```shell linenums="0"
ark exec dpa policies vm editor commit-policies
```

### Generate a short-lived SSO password for a database connection
```shell linenums="0"
ark exec dpa sso short-lived-password
```

### Generate a short-lived SSO Oracle wallet for an Oracle database connection
```shell linenums="0"
ark exec dpa sso short-lived-oracle-wallet --folder ~/wallet
```

### Generate a kubectl config file 
```shell linenums="0"
ark exec dpa k8s generate-kubeconfig 
```

### Generate a kubectl config file and save it in the specified path
```shell linenums="0"
ark exec dpa k8s generate-kubeconfig --folder=/Users/My.User/.kube
```
