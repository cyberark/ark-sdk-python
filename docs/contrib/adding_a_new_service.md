---
title: Adding a New Service
description: Adding a New Service
---

# Adding a New Service

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
