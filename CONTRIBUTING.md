# Contributing to CyberArk ark-sdk-python Check
👍🎉 First off, thanks for taking the time to contribute! 🎉👍

The following is a set of guidelines for contributing to the CyberArk ark-sdk-python. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

This repository is maintained by good people that take the time to make this tool better with best practices and not by official CyberArk R&D. 

For general contribution and community guidelines, please see the [community repo](https://github.com/cyberark/community).

## Table of Contents

- [Development](#development)
- [Testing](#testing)
- [Releases](#releases)
- [Contributing](#contributing)
	- [General Workflow](#general-workflow)
	- [Reporting Bugs](#reporting-bugs)

## Development

This tool is created under Python and can be cloned or installed via the community Pypi.
You should be familiar with Python before contibuting to this project.

### Adding a New API
Adding a new API to an existing service is fairly straight forward

Each API receives a model as an input and may choose one of the followings as an output:

- Model
- AsyncRequest
- Iterator[ArkPage]
- None

Once the input and output models were defined, we can add the model under the fitting service models folder in [models](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/services){:target="_blank" rel="noopener"}:

And afterwards add the request api itself in the fitting service, with the model used

If you want to expose it on the CLI as well, you may also add it to the relevant consts definition under [action_consts](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/actions/services)


### Adding a New Authenticator
To add a new authenticator, one must implement the following interface [ark_auth.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/auth/ark_auth.py){:target="_blank" rel="noopener"}:

```python
class ArkAuth(ABC):
    @abstractmethod
    def _perform_authentication(
        self, profile: ArkProfile, auth_profile: ArkAuthProfile, secret: Optional[ArkSecret] = None, force: bool = False
    ) -> ArkToken:
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

    @staticmethod
    @abstractmethod
    def authenticator_name() -> str:
        """
        Name of the authenticator to be used for the auth profiles and services

        Returns:
            str: _description_
        """

    @staticmethod
    @abstractmethod
    def authenticator_human_readable_name() -> str:
        """
        Human readable name of the authenticator to be used for representation to the user

        Returns:
            str: _description_
        """

    @staticmethod
    @abstractmethod
    def supported_auth_methods() -> List[ArkAuthMethod]:
        """
        Supported authenticaton methods by this authenticator

        Returns:
            List[ArkAuthMethod]: _description_
        """

    @staticmethod
    @abstractmethod
    def default_auth_method() -> Tuple[ArkAuthMethod, ArkAuthMethodSettings]:
        """
        Default authentication method used by this authenticator with its default settings

        Returns:
            Tuple[ArkAuthMethod, ArkAuthMethodSettings]: _description_
        """
```

The above will implement the authenticator logic itself, and all needed information about the authenticator

Once implemented, you may use it accordingly with the fitting services who need such authenticator

If you also wish to expose the authenticator to the CLI, u may also add him to the SUPPORTED_AUTHENTICATORS list under [auth/__init__.py](https://https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/auth/__init__.py){:target="_blank" rel="noopener"}:

Once added, it will be automatically exposed on configure and login actions

### Adding a New Service

To add a new service that can be executed, once must implement the following interface [ark_service.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/services/ark_service.py){:target="_blank" rel="noopener"}:

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

If you wish to expose it on the ArkAPI, add a property to the service on [ark_api.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/ark_api.py){:target="_blank" rel="noopener"}, such as the following:

```python
@property
def dpa_policies(self) -> "ArkDPAPoliciesService":
    """
    Returns the dpa policies service if the fitting authenticators were given

    Returns:
        ArkDPAPoliciesService: _description_
    """
    from ark_sdk_python.services.dpa.policies import ArkDPAPoliciesService

    return cast(ArkDPAPoliciesService, self.service(ArkDPAPoliciesService))
```

If you also wish to expose it on the CLI, you will need to add definitions to what exactly will be exposed, along with exposing it on the API
To expose an action to the cli, you can add a new consts definition for the service, under [action_consts](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/actions/services){:target="_blank" rel="noopener"}, definining its actions and schemas, and finally, expose it using the ArkServiceActionDefinition class

Once the definition is done, to automatically expose it, add the ArkServiceActionDefinition definition to [SUPPORTED_SERVICE_ACTIONS](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/actions/services/__init__.py){:target="_blank" rel="noopener"}


You may use the existing services as references


## Testing

You will be responsible testing your own code, please make sure to adhere to the functions naming convention and add the relevant documentation link if available along with adding information to the docs folder and unittests

## Contributing 

### General Workflow

1. [Fork the project](https://help.github.com/en/github/getting-started-with-github/fork-a-repo)
2. [Clone your fork](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository)
3. Make local changes to your fork by editing or creating new files
3. [Commit your changes](https://help.github.com/en/github/managing-files-in-a-repository/adding-a-file-to-a-repository-using-the-command-line)
4. [Push your local changes to the remote server](https://help.github.com/en/github/using-git/pushing-commits-to-a-remote-repository)
5. [Create new Pull Request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork)

From here your pull request will be reviewed and once you've responded to all feedback it will be merged into the project. 

Congratulations, you're a contributor! 🎉🎉🎉

### Reporting Bugs
This section guides you through submitting a bug report or an issue with one of the script published in this repository. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

When you are creating a bug report, please include as many details as possible and make sure you run the script with Verbose logging (In all commands, add -v after the subcommand).

**Note**: If you find a Closed issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

**Before Submitting A Bug Report**
Run the script with Verbose logging.
Perform a cursory search to see if the problem has already been reported. If it has and the issue is still open, add a comment to the existing issue instead of opening a new one.