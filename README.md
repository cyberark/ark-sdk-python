Ark SDK Python
=================

**[📜Documentation](https://pages.github.com/cyberark/ark-sdk-python/)**

![Ark SDK Python](https://github.com/cyberark/ark-sdk-python/blob/master/assets/sdk.png)

CyberArk's Official SDK and CLI for different services operations

## Features and Services
- [x] Extensive and Interactive CLI
- [x] Different Authenticators
    - [x] Identity Authentication Methods
    - [x] MFA Support for Identity
    - [x] Identity Security Platform
- [x] Services API
    - [x] DPA VM / Databases Policies and Policies Interactive Editor Service
    - [x] DPA Databases Onboarding
    - [x] DPA Databases Secrets
    - [x] DPA Certificates Service
    - [x] DPA SSO Service
    - [x] DPA K8S Service
    - [x] DPA Databases Service
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
![Ark SDK Enduser Usage](https://github.com/cyberark/ark-sdk-python/blob/master/assets/ark_sdk_enduser_tldr.gif)

## Admin
![Ark SDK Admin Usage](https://github.com/cyberark/ark-sdk-python/blob/master/assets/ark_sdk_admin_tldr.gif)



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
- <b>dpa</b> - Dynamic Privilege Access Services
    - <b>policies</b> - DPA Policies Management
        - <b>vm</b> - DPA VM Policies Service
            - <b>editor</b> - DPA Policies Interactive Editor
        - <b>db</b> - DPA DB Policies Service
            - <b>editor</b> - DPA Policies Interactive Editor
    - <b>workspaces</b> - DPA Workspaces Management
        - <b>db</b> - DPA DB Workspace Service
    - <b>secrets</b> - DPA Secrets / Strong Accounts Management
        - <b>db</b> - DPA DB Secrets Service
    - <b>certificates</b> - DPA Certificates Management
    - <b>databases</b> - DPA Databases Enduser Operations
    - <b>sso</b> - DPA SSO Enduser Operations
    - <b>k8s</b> - DPA kubernetes service

Any command has its own subcommands, with respective arguments

For example configure a profile to login to that respective tenant and perform DPA actions such as:

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

For example, let's say we want to create a demo environment containing all needed DPA DB assets

To do so, we can use the following script:

```python
ArkSystemConfig.disable_verbose_logging()
# Authenticate to the tenant with an auth profile to configure DPA
username = 'user@cyberark.cloud.12345'
print(f'Authenticating to the created tenant with user [{username}]')
isp_auth = ArkISPAuth()
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
    ),
    secret=ArkSecret(secret='CoolPassword'),
)

# Create DPA DB Secret, Database, Connector and DB Policy
dpa_service = ArkDPAAPI(isp_auth)
print('Adding DPA DB User Secret')
secret = dpa_service.secrets_db.add_secret(
    ArkDPADBAddSecret(secret_type=ArkDPADBSecretType.UsernamePassword, username='Administrator', password='CoolPassword')
)
print('Adding DPA Database')
dpa_service.workspace_db.add_database(
    ArkDPADBAddDatabase(
        name='mydomain.com',
        provider_engine=ArkDPADBDatabaseEngineType.PostgresSH,
        secret_id=secret.secret_id,
        read_write_endpoint="myendpoint.mydomain.com",
    )
)
print('Adding DPA DB Policy')
dpa_service.policies_db.add_policy(
    ArkDPADBAddPolicy(
        policy_name='IT Policy',
        status=ArkDPARuleStatus.Active,
        description='IT Policy',
        providers_data=ArkDPADBProvidersData(
            postgres=ArkDPADBPostgres(
                resources=['postgres-onboarded-asset'],
            ),
        ),
        user_access_rules=[
            ArkDPADBAuthorizationRule(
                rule_name='IT Rule',
                user_data=ArkDPAUserData(roles=['DpaAdmin'], groups=[], users=[]),
                connection_information=ArkDPADBConnectionInformation(
                    grant_access=2,
                    idle_time=10,
                    full_days=True,
                    hours_from='07:00',
                    hours_to='17:00',
                    time_zone='Asia/Jerusalem',
                    connect_as=ArkDPADBConnectAs(
                        db_auth=[
                            ArkDPADBLocalDBAuth(
                                roles=['rds_superuser'],
                                applied_to=[
                                    ArkDPADBAppliedTo(
                                        name='postgres-onboarded-asset',
                                        type=ArkDPADBResourceIdentifierType.RESOURCE,
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


Contributing
============
Contributing new services or authenticators requires implementing different interfaces per the required purpose

Adding a new authenticator
--------------------------
To add a new authenticator, one must implement the following interface under auth/ark_auth.py:
```python
class ArkAuth(ABC):
    @abstractmethod
    def _perform_authentication(self, profile: ArkProfile, auth_profile: ArkAuthProfile, 
                                secret: Optional[ArkSecret] = None, force: bool = False) -> ArkToken:
        """
        Performs the actual authentication, based on the implementation

        Args:
            profile (ArkProfile): Profile to authenticate on
            auth_profile (ArkAuthProfile): Specific auth profile for the authentication
            secret (Optional[ArkSecret]): Secret used for authentication. Defaults to None
            force (bool): Force authenticate and ignore caching

        Returns:
            Optional[ArkToken]: Token of the authentication to be used
        """
        pass

    @staticmethod
    @abstractmethod
    def authenticator_name() -> str:
        """
        Name of the authenticator to be used for the auth profiles and services

        Returns:
            str: 
        """
        pass

    @staticmethod
    @abstractmethod
    def authenticator_human_readable_name() -> str:
        """
        Human readable name of the authenticator to be used for representation to the user

        Returns:
            str: 
        """
        pass

    @staticmethod
    @abstractmethod
    def supported_auth_methods() -> List[ArkAuthMethod]:
        """
        Supported authenticaton methods by this authenticator

        Returns:
            List[ArkAuthMethod]
        """
        pass

    @staticmethod
    @abstractmethod
    def default_auth_method() -> Tuple[ArkAuthMethod, ArkAuthMethodSettings]:
        """
        Default authentication method used by this authenticator

        Returns:
            Tuple[ArkAuthMethod, ArkAuthMethodSettings]
        """
        pass
```

The above will implement the authenticator logic itself, and all needed information about the authenticator

Once implemented, you may use it accordingly with the fitting services who need such authenticator

If you also wish to expose the authenticator to the CLI, u may also add him to the SUPPORTED_AUTHENTICATORS list under auth/__init__.py

Once added, it will be automatically exposed on configure and login actions


Adding a new service
--------------------
To add a new service that can be executed, once must implement the following interface under services/ark_service.py:

```python
class ArkService(ABC):
    @staticmethod
    @abstractmethod
    def service_config() -> ArkServiceConfig:
        """
        Returns the service config containing the service name, and required / optional authenticators

        Returns:
            ArkServiceConfig
        """
        pass
```
The only required thing from the service is to expose its configuration

Any other action on the service is implemented explictly

Once implemented, you can use it along with the fitting authenticators

If you wish to expose it on the api, add a property to the service, and add it to the SUPPORTED_SERVICES list

If you also wish to expose it on the CLI, you will need to add definitions to what exactly will be exposed, along with exposing it on the API
To expose an action to the cli, you can add a new consts definition for the service, under modes/actions/services, definining its actions and schemas, and finally, expose it using the ArkServiceActionDefinition class

Once the definition is done, to automatically expose it, add the ArkServiceActionDefinition definition to SUPPORTED_SERVICE_ACTIONS

You may use the existing services as references
