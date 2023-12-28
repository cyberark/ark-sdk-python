---
title: Schemas
description: Schemas
---

# Schemas

Ark SDK is entirely based on schemas constructed from [Pydantic](https://docs.pydantic.dev/){:target="_blank" rel="noopener"}. Pydantic is a schema and data validation library that also provides settings management and uses Python type annotations.

All `exec` actions in the Ark SDK receive a model parsed from the CLI or from the SDK in code and, some of them, return a model or set of models. All of these models inherit from ArkModel:

```python
class ArkModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
```

Derived from the model above, there are different model types that serve different purposes, such as aliasing attributes with camelCase and adding polling parameters.

## Example

Any request can be called with a defined model, for example:

```python
policies_service = ArkDPADBPoliciesService(isp_auth)
policies = policies_service.list_policies()
```

The above example creates a DB policies service and calls `list_policies()` to retrieve a list of all tenant DB polices. The returned list items contain `policy_id` and `policy_name` fields, which can be used with the ArkDPAGetPolicy model:

```python
class ArkDPAGetPolicy(ArkModel):
    policy_id: Optional[str] = Field(description='Policy id to get')
    policy_name: Optional[str] = Field(description='Policy name to get')

```

All models can be found [here](https://github.com/cyberark/ark-sdk-python/tree/master/ark_sdk_python/models) and are separated to folders based on topic, from auth to services
