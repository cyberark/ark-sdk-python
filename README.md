![Ark SDK Python](https://github.com/cyberark/ark-sdk-python/blob/main/assets/sdk.png)

<p align="center">
    <a href="https://actions-badge.atrox.dev/cyberark/ark-sdk-python/goto?ref=main" alt="Build">
        <img src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fcyberark%2Fark-sdk-python%2Fbadge%3Fref%3Dmain&style=flat" />
    </a>
    <a href="https://pypi.python.org/pypi/ark-sdk-python/" alt="Python Versions">
        <img src="https://img.shields.io/pypi/pyversions/ark-sdk-python.svg?style=flat" />
    </a>
    <a href="https://pypi.python.org/pypi/ark-sdk-python/" alt="Package Version">
        <img src="http://img.shields.io/pypi/v/ark-sdk-python.svg?style=flat" />
    </a>
    <a href="https://github.com/cyberark/ark-sdk-python/blob/main/LICENSE.txt" alt="License">
        <img src="http://img.shields.io/pypi/l/ark-sdk-python.svg?style=flat" />
    </a>
</p>

Ark SDK Python 
==============

📜[**Documentation**](https://cyberark.github.io/ark-sdk-python/)

CyberArk's Official SDK and CLI for different services operations

## Features and Services
- [x] Extensive and Interactive CLI
- [x] Different Authenticators
    - [x] Identity Authentication Methods
    - [x] MFA Support for Identity
    - [x] Identity Security Platform
- [x] Services API
    - [x] SIA VM / Databases Policies and Policies Interactive Editor Service
    - [x] SIA Databases Onboarding
    - [x] SIA Target Sets Onboarding
    - [x] SIA Databases Secrets
    - [x] SIA VM Secrets
    - [x] SIA Certificates Service
    - [x] SIA SSO Service
    - [x] SIA K8S Service
    - [x] SIA DB Service
    - [x] SIA Access Service
    - [x] SIA SSH CA Service
    - [x] Session Monitoring Service
    - [x] Identity Users Service
    - [x] Identity Roles Service
    - [x] Identity Policies Service
    - [x] Identity Directories Service
    - [x] Identity Connectors Service
    - [x] PCloud Accounts Service
    - [x] PCloud Safes Service
    - [x] PCloud Platforms Service
    - [x] PCloud Applications Service
    - [x] Connector Manager Service
    - [x] Unified Access Policies Service
        - [x] SCA - Secure Cloud Access
        - [x] DB - Databases
        - [x] VM - Virtual Machines
- [x] All services contains CRUD and Statistics per respective service
- [x] Ready to use SDK in Python
- [x] CLI and SDK Examples
- [x] Fully Interactive CLI comprising of 3 main actions
    - [x] Configure
    - [x] Login
    - [x] Exec
- [x] Filesystem Inputs and Outputs for the CLI
- [x] Silent and Verbose logging
- [x] Profile Management and Authentication Caching


TL;DR
=====

## Enduser
![Ark SDK Enduser Usage](https://github.com/cyberark/ark-sdk-python/blob/main/assets/ark_sdk_enduser_tldr.gif)

## Admin
![Ark SDK Admin Usage](https://github.com/cyberark/ark-sdk-python/blob/main/assets/ark_sdk_admin_tldr.gif)



Installation
============

One can install the SDK via the community pypi with the following command:
```shell
pip3 install ark-sdk-python
```

CLI Usage
============
Both the SDK and the CLI works with profiles

The profiles can be configured upon need and be used for the consecutive actions

The CLI has the following basic commands:
- <b>configure</b> - Configures profiles and their respective authentication methods
- <b>login</b> - Logs into the profile authentication methods
- <b>exec</b> - Executes different commands based on the supported services
- <b>profiles</b> - Manage multiple profiles on the machine


configure
---------
The configure command is used to create a profile to work on<br>
The profile consists of infomration regarding which authentication methods to use and what are their method settings, along with other related information such as MFA

How to run:
```shell
ark configure
```


The profiles are saved to ~/.ark_profiles

No arguments are required, and interactive questions will be asked

If you wish to only supply arguments in a silent fashion, --silent can be added along with the arugments

Usage:
```shell
usage: ark configure [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                     [-dcv] [-tc TRUSTED_CERT] [-pn PROFILE_NAME] [-pd PROFILE_DESCRIPTION] [-wwis]
                     [-isam {identity,identity_service_user}] [-iu ISP_USERNAME]
                     [-iimm {pf,sms,email,otp}] [-iiu ISP_IDENTITY_URL]
                     [-iiaa ISP_IDENTITY_AUTHORIZATION_APPLICATION]

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             Whether to raw output
  -s, --silent          Silent execution, no interactiveness
  -ao, --allow-output   Allow stdout / stderr even when silent and not interactive
  -v, --verbose         Whether to verbose log
  -ls {default}, --logger-style {default}
                        Which verbose logger style to use
  -ll {DEBUG,INFO,WARN,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        Log level to use while verbose
  -dcv, --disable-cert-verification
                        Disables certificate verification on HTTPS calls, unsafe!
  -tc TRUSTED_CERT, --trusted-cert TRUSTED_CERT
                        Certificate to use for HTTPS calls
  -pn PROFILE_NAME, --profile-name PROFILE_NAME
                        Profile name for storage
  -pd PROFILE_DESCRIPTION, --profile-description PROFILE_DESCRIPTION
                        Info about the profile
  -wwis, --work-with-isp
                        Whether to work with Identity Security Platform services
  -isam {identity,identity_service_user}, --isp-auth-method {identity,identity_service_user}
  -iu ISP_USERNAME, --isp-username ISP_USERNAME
                        Username to authenticate with
  -iimm {pf,sms,email,otp}, --isp-identity-mfa-method {pf,sms,email,otp}
                        MFA method if mfa is needed
  -iiu ISP_IDENTITY_URL, --isp-identity-url ISP_IDENTITY_URL
                        Identity url to use for authentication instead of fqdn resolving
  -iiaa ISP_IDENTITY_AUTHORIZATION_APPLICATION, --isp-identity-authorization-application ISP_IDENTITY_AUTHORIZATION_APPLICATION
                        Identity application to authorize once logged in with the service user
```


login
-----
The logn command is used to login to the authentication methods configured for the profile

You will be asked to write a password for each respective authentication method that supports password, and alongside that, any needed MFA prompt

Once the login is done, the access tokens are stored on the computer keystore for their lifetime

Once they are expired, a consecutive login will be required

How to run:
```shell
ark login
```

Usage:
```shell
usage: ark login [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}]
                 [-dcv] [-tc TRUSTED_CERT] [-pn PROFILE_NAME] [-f] [-nss] [-st] [-ra]
                 [-isu ISP_USERNAME] [-iss ISP_SECRET]

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             Whether to raw output
  -s, --silent          Silent execution, no interactiveness
  -ao, --allow-output   Allow stdout / stderr even when silent and not interactive
  -v, --verbose         Whether to verbose log
  -ls {default}, --logger-style {default}
                        Which verbose logger style to use
  -ll {DEBUG,INFO,WARN,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        Log level to use while verbose
  -dcv, --disable-cert-verification
                        Disables certificate verification on HTTPS calls, unsafe!
  -tc TRUSTED_CERT, --trusted-cert TRUSTED_CERT
                        Certificate to use for HTTPS calls
  -pn PROFILE_NAME, --profile-name PROFILE_NAME
                        Profile name to load
  -f, --force           Whether to force login even thou token has not expired yet
  -nss, --no-shared-secrets
                        Do not share secrets of identity between different authenticators with the
                        same username
  -st, --show-tokens    Print out tokens as well if not silent
  -ra, --refresh-auth   If a cache exists, will also try to refresh it
  -isu ISP_USERNAME, --isp-username ISP_USERNAME
                        Username to authenticate with to Identity Security Platform
  -iss ISP_SECRET, --isp-secret ISP_SECRET
                        Secret to authenticate with to Identity Security Platform
```

Notes:

- You may disable certificate validation for login to different authenticators using the --disable-certificate-verification or supply a certificate to be used, not recommended to disable


exec
----
The exec command is used to execute various commands based on supported services for the fitting logged in authenticators

The following services and commands are supported:
- <b>sia</b> - Dynamic Privilege Access Services
    - <b>policies</b> - SIA Policies Management
        - <b>vm</b> - SIA VM Policies Service
            - <b>editor</b> - SIA Policies Interactive Editor
        - <b>db</b> - SIA DB Policies Service
            - <b>editor</b> - SIA Policies Interactive Editor
    - <b>workspaces</b> - SIA Workspaces Management
        - <b>db</b> - SIA DB Workspace Service
        - <b>target-sets</b> - SIA Target Sets Workspace Service
    - <b>secrets</b> - SIA Secrets / Strong Accounts Management
        - <b>db</b> - SIA DB Secrets Service
        - <b>vm</b> - SIA VM Secrets Service
    - <b>certificates</b> - SIA Certificates Management
    - <b>db</b> - SIA DB Enduser Operations
    - <b>sso</b> - SIA SSO Enduser Operations
    - <b>k8s</b> - SIA Kubernetes Service
    - <b>access</b> - SIA Access Service
    - <b>ssh-ca</b> - SIA SSH CA Service
- <b>sm</b> - Session Monitoring Service
- <b>identity</b> - Identity Service
    - <b>users</b> - Identity Users Management
    - <b>roles</b> - Identity Roles Management
    - <b>policies</b> - Identity Policies Management
    - <b>directories</b> - Identity Directories Reading
- <b>pcloud</b> - PCloud Service
    - <b>accounts</b> - PCloud Accounts Management
    - <b>safes</b> - PCloud Safes Management
    - <b>platforms</b> - PCloud Platforms Management
    - <b>applications</b> - PCloud Applications Management
- <b>cmgr</b> - Connector Manager Service
- <b>uap</b> - Unified Access Policies Services
    - <b>sca</b> - secure cloud access policies management
    - <b>db</b> - databases access policies management
    - <b>vm</b> - virtual machines access policies management

Any command has its own subcommands, with respective arguments

For example configure a profile to login to that respective tenant and perform SIA actions such as:

Add SIA Database Secret
```shell
ark exec sia secrets db add-secret --secret-name mysecret --secret-type username_password --username user --password mypass
```

Delete SIA Database Secret
```shell
ark exec sia secrets db delete-secret --secret-name mysecret
```

Add SIA Database
```shell
ark exec sia workspaces db add-database --name mydb --provider-engine postgres-sh --read-write-endpoint myendpoint.domain.com
```

List SIA Databases
```shell
ark exec sia workspaces db list-databases
```

Get VM policies stats
```shell
ark exec sia policies vm policies-stats
```

Add SIA VM Target Set
```shell
ark_public exec sia workspaces target-sets add-target-set --name mydomain.com --type Domain
```

Add SIA VM Secret
```shell
ark_public exec sia secrets vm add-secret --secret-type ProvisionerUser --provisioner-username=myuser --provisioner-password=mypassword
```

Edit policies interactively

This gives the ability to locally work with a policies workspace, and edit / reset / create policies, applied to both databases and vm policies

When they are ready, once can commit all the policies changes to the remote

Initially, the policies can be loaded and reloaded using

```shell
ark exec sia policies vm editor load-policies
```

Once they are loaded locally, they can be edited using the following commands
```shell
ark exec sia policies vm editor edit-policies
ark exec sia policies vm editor view-policies
ark exec sia policies vm editor reset-policies
ark exec sia policies vm editor generate-policy
ark exec sia policies vm editor remove-policies
ark exec sia policies vm editor policies diff
```

Evantually, they can be committed using
```shell
ark exec sia policies vm editor commit-policies
```

Generate a short lived SSO password for databases connection
```shell
ark exec sia sso short-lived-password
```

Generate a short lived SSO password for RDP connection
```shell
ark exec sia sso short-lived-password --service DPA-RDP
```

Generate a short lived SSO oracle wallet for oracle database connection
```shell
ark exec sia sso short-lived-oracle-wallet --folder ~/wallet
```

Generate kubectl config file 
```shell
ark exec sia k8s generate-kubeconfig 
```

Generate kubectl config file and save on specific path
```shell
ark exec sia k8s generate-kubeconfig --folder=/Users/My.User/.kube
```

Generate new SSH CA Key version
```shell
ark exec sia ssh-ca generate-new-ca
```

Deactivate previous SSH CA Key version
```shell
ark exec sia ssh-ca deactivate-previous-ca
```

Reactivate previous SSH CA Key version
```shell
ark exec sia ssh-ca reactivate-previous-ca
```

Get SSH CA public key
```shell
ark exec sia ssh-ca public-key
```

Get SSH CA public key script
```shell
ark exec sia ssh-ca public-key-script
```

Create a PCloud Safe
```shell
ark exec pcloud safes add-safe --safe-name=safe
```

Create a PCloud Account
```shell
ark exec pcloud accounts add-account --name account --safe-name safe --platform-id='UnixSSH' --username root --address 1.2.3.4 --secret-type=password --secret mypass
```

List available platforms
```shell
ark exec pcloud platforms list-platforms
```

List connector pools
```shell
ark exec exec cmgr list-pools
```

Get connector installation script
```shell
ark exec sia access connector-setup-script -ct onprem -co windows -cpi 588741d5-e059-479d-b4c4-3d821a87f012
```

List UAP policies
```shell
ark exec uap list-policies
```

Get UAP policy
```shell
ark exec uap policy --policy-id my-policy-id
```

Delete UAP Policy
```shell
ark exec uap delete-policy --policy-id my-policy-id
```

List DB Policies from UAP
```shell
ark exec uap db list-policies
```

Get DB Policy from UAP
```shell
ark exec uap db policy --policy-id my-policy-id
```

Delete DB Policy from UAP
```shell
ark exec uap db delete-policy --policy-id my-policy-id
```

List SCA Policies from UAP
```shell
ark exec uap sca list-policies
```

Get SCA Policy from UAP
```shell
ark exec uap sca policy --policy-id my-policy-id
```

Delete SCA Policy from UAP
```shell
ark exec uap sca delete-policy --policy-id my-policy-id
```

List VM Policies from UAP
```shell
ark exec uap vm list-policies
```

Get VM Policy from UAP
```shell
ark exec uap vm policy --policy-id my-policy-id
```

Delete VM Policy from UAP
```shell
ark exec uap vm delete-policy --policy-id my-policy-id
```

You can view all of the commands via the --help for each respective exec action

Notes:

- You may disable certificate validation for login to different authenticators using the --disable-certificate-verification or supply a certificate to be used, not recommended to disable


Usafe Env Vars:
- ARK_PROFILE - Sets the profile to be used across the CLI
- ARK_DISABLE_CERTIFICATE_VERIFICATION - Disables certificate verification on REST API's


profiles
-------
As one may have multiple environments to manage, this would also imply that multiple profiles are required, either for multiple users in the same environment or multiple tenants

Therefore, the profiles command manages those profiles as a convenice set of methods

Using the profiles as simply running commands under:
```shell
ark profiles
```

Usage:
```shell
usage: ark profiles [-h] [-r] [-s] [-ao] [-v] [-ls {default}] [-ll {DEBUG,INFO,WARN,ERROR,CRITICAL}] [-dcv]
                    [-tc TRUSTED_CERT]
                    {list,show,delete,clear,clone,add} ...

positional arguments:
  {list,show,delete,clear,clone,add}
    list                List all profiles
    show                Show a profile
    delete              Delete a specific profile
    clear               Clear all profiles
    clone               Clones a profile
    add                 Adds a profile to the profiles folder from a given path

optional arguments:
  -h, --help            show this help message and exit
  -r, --raw             Whether to raw output
  -s, --silent          Silent execution, no interactiveness
  -ao, --allow-output   Allow stdout / stderr even when silent and not interactive
  -v, --verbose         Whether to verbose log
  -ls {default}, --logger-style {default}
                        Which verbose logger style to use
  -ll {DEBUG,INFO,WARN,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        Log level to use while verbose
  -dcv, --disable-cert-verification
                        Disables certificate verification on HTTPS calls, unsafe!
  -tc TRUSTED_CERT, --trusted-cert TRUSTED_CERT
                        Certificate to use for HTTPS calls
```

SDK Usage
=========
As well as using the CLI, one can also develop under the ark sdk using its API / class driven design

The same idea as the CLI applies here as well

For example, let's say we want to create a demo environment containing all needed SIA DB assets

To do so, we can use the following script:

```python
ArkSystemConfig.disable_verbose_logging()
# Authenticate to the tenant with an auth profile to configure SIA
username = 'user@cyberark.cloud.12345'
print(f'Authenticating to the created tenant with user [{username}]')
isp_auth = ArkISPAuth()
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
    ),
    secret=ArkSecret(secret='CoolPassword'),
)

# Create SIA DB Secret, Database, Connector and DB Policy
sia_service = ArkSIAAPI(isp_auth)
print('Adding SIA DB User Secret')
secret = sia_service.secrets_db.add_secret(
    ArkSIADBAddSecret(secret_type=ArkSIADBSecretType.UsernamePassword, username='Administrator', password='CoolPassword')
)
print('Adding SIA Database')
sia_service.workspace_db.add_database(
    ArkSIADBAddDatabase(
        name='mydomain.com',
        provider_engine=ArkSIADBDatabaseEngineType.PostgresSH,
        secret_id=secret.secret_id,
        read_write_endpoint="myendpoint.mydomain.com",
    )
)
print('Installing SIA Connector')
sia_service.access.install_connector(
    ArkSIAInstallConnector(
        connector_os=ArkOsType.LINUX,
        connector_type=ArkWorkspaceType.ONPREM,
        connector_pool_id='pool_id',
        target_machine='1.2.3.4',
        username='root',
        private_key_path='/path/to/private.pem',
    )
)
print('Adding SIA DB Policy')
sia_service.policies_db.add_policy(
    ArkSIADBAddPolicy(
        policy_name='IT Policy',
        status=ArkSIARuleStatus.Enabled,
        description='IT Policy',
        providers_data=ArkSIADBProvidersData(
            postgres=ArkSIADBPostgres(
                resources=['postgres-onboarded-asset'],
            ),
        ),
        user_access_rules=[
            ArkSIADBAuthorizationRule(
                rule_name='IT Rule',
                user_data=ArkSIAUserData(roles=['DpaAdmin'], groups=[], users=[]),
                connection_information=ArkSIADBConnectionInformation(
                    grant_access=2,
                    idle_time=10,
                    full_days=True,
                    hours_from='07:00',
                    hours_to='17:00',
                    time_zone='Asia/Jerusalem',
                    connect_as=ArkSIADBConnectAs(
                        db_auth=[
                            ArkSIADBLocalDBAuth(
                                roles=['rds_superuser'],
                                applied_to=[
                                    ArkSIADBAppliedTo(
                                        name='postgres-onboarded-asset',
                                        type=ArkSIADBResourceIdentifierType.RESOURCE,
                                    )
                                ],
                            ),
                        ],
                    ),
                ),
            )
        ],
    )
)
```

More examples can be found in the examples folder

## License

This project is licensed under Apache License 2.0 - see [`LICENSE`](LICENSE.txt) for more details

Copyright (c) 2023 CyberArk Software Ltd. All rights reserved.
