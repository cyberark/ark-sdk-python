---
title: Architecture
description: Architecture
---

# Architecture

The design of the library is as follows:

![Ark SDK Design](./media/ark_sdk_design.png){: style="height:100%;width:100%"}

## Design Perspectives
We define the main entities as follows:

- <b>Profile</b> - A profile defines a set of properties and information about the authentication methods of the user, the profile is saved on the filesystem to be used for consecutive actions
- <b>Authenticators</b> - An integration with some authentication method, in order to be able to interact with a service in an authenticated manner, an authentication method can be one of the following or custom implemented:
    - Identity (User / Service User)
- <b>Services</b> - The actual service that gives some capabilities, and requires one or more authenticators in order to perform actions, such service can be for example the audit service, exposing different api's of the audit service in an authenticated manner
- <b>Services Model Schemes</b> - Each service also exposes different models and structures to be able to work with the service actions
- <b>CLI Actions</b> - All of the above defines the layers for the SDK, on top of that, the CLI actions gives a layer of interaction with the user via his shell, for the following actions:
    - configure - Configures a profile with all the details
    - login - Logins to the profile authenticators, with fitting required passwords etc, the logged in details are stored on the machine in a secure manner for consecutive actions
    - exec - Executes different services actions

## Typical Flow
A typical workflow would be to define a profile using the configure command, an then login to the profile authenticators.

Once logged in, execute actions based on the logged in authenticators