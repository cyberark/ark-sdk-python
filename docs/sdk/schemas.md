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
identity_api = ArkIdentityAPI(isp_auth)
role: ArkIdentityRole = identity_api.identity_roles.create_role(ArkIdentityCreateRole(role_name='IT'))
```

In the above example, we create the identity service, and call create_role, passing the ArkIdentityCreateRole model, which is based on the model, and returns an ArkIdentityRole model

Where the models are specified as follows:
```python
class ArkIdentityCreateRole(ArkModel):
    role_name: str = Field(description='Role name to create')
    admin_rights: List[ArkIdentityAdminRights] = Field(description='Admin rights to add to the role', default_factory=list)


class ArkIdentityRole(ArkModel):
    role_id: str = Field(description='Identifier of the role')
    role_name: str = Field(description='Name of the role')
```

All models can be found [here](https://github.com/cyberark/ark-sdk-python/tree/main/ark_sdk_python/models) and are separated to folders based on topic, from auth to services
