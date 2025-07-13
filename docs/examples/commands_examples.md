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

### Add SIA database secret

```shell linenums="0"
ark exec sia secrets db add-secret --secret-name mysecret --secret-type username_password --username user --password mypass
```

### Delete SIA database secret

```shell linenums="0"
ark exec sia secrets db delete-secret --secret-name mysecret
```

### Add SIA database

```shell linenums="0"
ark exec sia workspaces db add-database --name mydb --provider-engine postgres-sh --read-write-endpoint myendpoint.domain.com
```

### List SIA databases

```shell linenums="0"
ark exec sia workspaces db list-databases
```

### Get VM policies stats

```shell linenums="0"
ark exec sia policies vm policies-stats
```

### Edit policies interactively example

This example shows how to locally work with a policies workspace, and edit, reset, and create policies that are applied to both databases and VM policies. After the local policies are ready, you can commit all the policies changes to the remote workspace.

To load and reload policies locally:

```shell linenums="0"
ark exec sia policies vm editor load-policies
```

After loading the policies, use these commands to edit them:
```shell
ark exec sia policies vm editor edit-policies
ark exec sia policies vm editor view-policies
ark exec sia policies vm editor reset-policies
ark exec sia policies vm editor generate-policy
ark exec sia policies vm editor remove-policies
ark exec sia policies vm editor policies diff
```

When they are ready to be committed, run:
```shell linenums="0"
ark exec sia policies vm editor commit-policies
```

### Generate a short-lived SSO password for a database connection
```shell linenums="0"
ark exec sia sso short-lived-password
```

### Generate a short lived SSO password for RDP connection
```shell
ark exec sia sso short-lived-password --service DPA-RDP
```

### Generate a short-lived SSO Oracle wallet for an Oracle database connection
```shell linenums="0"
ark exec sia sso short-lived-oracle-wallet --folder ~/wallet
```

### Generate a kubectl config file 
```shell linenums="0"
ark exec sia k8s generate-kubeconfig 
```

### Generate a kubectl config file and save it in the specified path
```shell linenums="0"
ark exec sia k8s generate-kubeconfig --folder=/Users/My.User/.kube
```

### Add SIA VM Target Set
```shell
ark_public exec sia workspaces target-sets add-target-set --name mydomain.com --type Domain
```

### Add SIA VM Secret
```shell
ark_public exec sia secrets vm add-secret --secret-type ProvisionerUser --provisioner-username=myuser --provisioner-password=mypassword
```

### Get SIA connector installation script
```shell
ark exec sia access connector-setup-script -ct onprem -co windows -cpi 588741d5-e059-479d-b4c4-3d821a87f012
```

### Install a DPA Windows Connector Remotely
```shell
ark exec sia access install-connector --connector-pool-id abcd --connector-type onprem --connector-os windows --target-machine 1.2.3.4 --username myuser --password mypassword
```

### Install a DPA Linux Connector Remotely
```shell
ark exec sia access install-connector --connector-pool-id abcd --connector-type aws --connector-os linux --target-machine 1.2.3.4 --username ec2-user --private-key-path /path/to/key.pem
```

### Delete and uninstall a DPA Connector
```shell
ark exec sia access delete-connector --connector-id=CMSConnector_e9685e0d-a92e-4097-ad4d-b54eadb69bcb_81fa03c5-d0d3-4157-95f8-6a1903900fa0 --uninstall-connector --target-machine 1.2.3.4 --username ec2-user --private-key-path /path/to/key.pem
```

### Generate new SSH CA Key version
```shell
ark exec sia ssh-ca generate-new-ca
```

### Deactivate previous SSH CA Key version
```shell
ark exec sia ssh-ca deactivate-previous-ca
```

### Reactivate previous SSH CA Key version
```shell
ark exec sia ssh-ca reactivate-previous-ca
```

### Get SSH CA public key
```shell
ark exec sia ssh-ca public-key
```

### Get SSH CA public key script
```shell
ark exec sia ssh-ca public-key-script
```

### List All Session Monitoring sessions from the last 24 hours
```shell
ark exec sm list-sessions
```

### Count All Session Monitoring sessions from the last 24 hours
```shell
ark exec sm count-sessions
```

### List All Session Monitoring sessions matching Search Query
```shell
ark exec sm list-sessions-by --search 'startTime ge 2023-12-03T08:55:29Z AND sessionDuration GE 00:00:01 AND protocol IN SSH,RDP,Database'
```

### Count All Session Monitoring sessions matching Search Query
```shell
ark exec sm count-sessions-by --search 'startTime ge 2023-12-03T08:55:29Z AND sessionDuration GE 00:00:01 AND protocol IN SSH,RDP,Database'
```

### Count All Session Monitoring sessions from the last 24 hours
```shell
ark exec sm count-sessions
```

### Retrieve a session by id
```shell
ark exec sm session --session-id 5e62bdb8-cd81-42b8-ac72-1e06bf9c496d
```

### List all session activities
```shell
ark exec sm list-session-activities --session-id 5e62bdb8-cd81-42b8-ac72-1e06bf9c496d
```

### Count all session activities
```shell
ark exec sm count-session-activities --session-id 5e62bdb8-cd81-42b8-ac72-1e06bf9c496d
```

### List all session activities with specific command
```shell
ark exec sm list-session-activities-by --session-id 5e62bdb8-cd81-42b8-ac72-1e06bf9c496d --command-contains 'ls'
```

### Count all session activities with specific command
```shell
ark exec sm count-session-activities-by --session-id 5e62bdb8-cd81-42b8-ac72-1e06bf9c496d --command-contains 'ls'
```

### Display general sessions statistics from the last 30 days
```shell
ark exec sm sessions-stats
```

### List all identity entities, including roles users and groups
```shell
ark exec identity directories list-directories-entities
```

### List only identity roles
```shell
ark exec identity directories list-directories-entities --entity-types ROLE
```

### Create a role with SIA show tile admin right
```shell
ark exec identity roles create-role --role-name RoleName --admin-rights "ServiceRight/dpaShowTile"
```

### Delete a role by name
```shell
ark exec identity roles delete-role --role-name RoleName
```

### Create a new user
```shell
ark exec identity users create-user --username myname --email email@email.com --password MyPassword
```

### Delete a user by name
```shell
ark exec identity users delete-user --username myname
```

### Add an authentication profile
```shell
ark exec identity policies add-authentication-profile --auth-profile-name myprofile --first-challenges UP --second-challenges EMAIL
```

### Add a policy
```shell
ark exec identity policies add-policy --policy-name mypolicy --role-names RoleName --auth-profile-name myprofile
```

### Create a PCloud Safe
```shell
ark exec pcloud safes add-safe --safe-name=safe
```

### Create a PCloud Account
```shell
ark exec pcloud accounts add-account --name account --safe-name safe --platform-id='UnixSSH' --username root --address 1.2.3.4 --secret-type=password --secret mypass
```

### List available platforms
```shell
ark exec pcloud platforms list-platforms
```

### List CMGR connector pools
```shell
ark exec cmgr list-pools
```

### Add CMGR network
```shell
ark exec cmgr add-network --name mynetwork
```

### Add CMGR connector pool
```shell
ark exec cmgr add-pool --name mypool --assigned-network-ids mynetwork_id
```
