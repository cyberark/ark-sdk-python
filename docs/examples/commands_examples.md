---
title: Commands Examples
description: Commands Examples
---

# Commands Examples
As a CLI user, there are many different actions that can be done under many different services

## Configure Commands Examples
The configure command can work interactive or silent, an example of configuring ISP in a silent fashion:

```bash
ark configure --profile-name="PROD" --work-with-isp --isp-username="tina@cyberark.cloud.12345" --silent --allow-output
```

## Login Commands Examples
The login command can work interactive or silent, example of logging in in a silent fashion to the above configure example:
```bash
ark login -s --isp-secret=CoolPassword
```

## Exec Commands Examples
Add DPA Database Secret
```shell
ark exec dpa secrets db add-secret --secret-name mysecret --secret-type username_password --username user --password mypass
```

Delete DPA Database Secret
```shell
ark exec dpa secrets db delete-secret --secret-name mysecret
```

Add DPA Database
```shell
ark exec dpa workspaces db add-database --name mydb --provider-engine postgres-sh --read-write-endpoint myendpoint.domain.com
```

List DPA Databases
```shell
ark exec dpa workspaces db list-databases
```

Get VM policies stats
```shell
ark exec dpa policies vm policies-stats
```

Edit policies interactively

This gives the ability to locally work with a policies workspace, and edit / reset / create policies, applied to both databases and vm policies

When they are ready, once can commit all the policies changes to the remote

Initially, the policies can be loaded and reloaded using

```shell
ark exec dpa policies vm editor load-policies
```

Once they are loaded locally, they can be edited using the following commands
```shell
ark exec dpa policies vm editor edit-policies
ark exec dpa policies vm editor view-policies
ark exec dpa policies vm editor reset-policies
ark exec dpa policies vm editor generate-policy
ark exec dpa policies vm editor remove-policies
ark exec dpa policies vm editor policies diff
```

Evantually, they can be committed using
```shell
ark exec dpa policies vm editor commit-policies
```

Generate a short lived SSO password for databases connection
```shell
ark exec dpa sso short-lived-password
```

Generate a short lived SSO oracle wallet for oracle database connection
```shell
ark exec dpa sso short-lived-oracle-wallet --folder ~/wallet
```

Generate kubectl config file 
```shell
ark exec dpa k8s generate-kubeconfig 
```

Generate kubectl config file and save on specific path
```shell
ark exec dpa k8s generate-kubeconfig --folder=/Users/My.User/.kube
```

You can view all of the commands via the --help for each respective exec action

Notes:

- You may disable certificate validation for login to different authenticators using the --disable-certificate-verification or supply a certificate to be used, not recommended to disable


Usafe Env Vars:
- ARK_PROFILE - Sets the profile to be used across the CLI
- ARK_DISABLE_CERTIFICATE_VERIFICATION - Disables certificate verification on REST API's
