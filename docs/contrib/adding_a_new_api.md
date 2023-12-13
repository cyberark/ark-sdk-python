---
title: Adding a New API
description: Adding a New API
---

# Adding a New API
Adding a new API to an existing service is fairly straight forward

Each API receives a model as an input and may choose one of the followings as an output:

- Model
- AsyncRequest
- Iterator[ArkPage]
- None

Once the input and output models were defined, we can add the model under the fitting service models folder in [models](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/services){:target="_blank" rel="noopener"}:

And afterwards add the request api itself in the fitting service, with the model used

If you want to expose it on the CLI as well, you may also add it to the relevant consts definition under [action_consts](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/models/actions/services)