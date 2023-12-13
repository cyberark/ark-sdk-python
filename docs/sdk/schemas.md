---
title: Schemas
description: Schemas
---

# Schemas

## Motivation
Ark SDK is entirely based on schemas that are constructed from [pydantic](https://docs.pydantic.dev/){:target="_blank" rel="noopener"}

Pydantic is a schema and data validation library and settings management using python type annotations

All of the exec actions in ark sdk receive a model either parsed from the CLI in a generic fashion or from the SDK in code, and some of them, also return a model or set of models as well

All of the models inherit from a base model called ArkModel

```python
class ArkModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
```

Following the above model, there are different types of models which serve different base purpose such as aliasing all the attributes with camelCase, or adding polling parameters to the model

## Example
Any request can be called with a fitting model, an example of that would be:

```python
policies_service = ArkDPADBPoliciesService(isp_auth)
policies = policies_service.list_policies()
```

In the above example, we create the identity service, and call create_role, passing the ArkIdentityCreateRole model, which is based on the model, and returns an ArkIdentityRole model

Where the models are specified as follows:
```python
class ArkDPDBAGetPolicy(ArkModel):
    policy_id: Optional[str] = Field(description='Policy id to get')
    policy_name: Optional[str] = Field(description='Policy name to get')

```

All of the models can be found [here](https://github.com/cyberark/ark-sdk-python/tree/master/ark_sdk_python/models) and are seperated to folders based on topic, from auth to services
