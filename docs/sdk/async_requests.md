---
title: Async Requests
description: Async Requests
---

# Async Requests

## Motivation
Some of the requests may be async requests, such as creating a tenant, and those requests do not end straight away

To support such a mechanism, API's that have this kind of behaviour can return an ArkAsyncRequest

The request implements the following interface
```python
@abstractmethod
def is_finished(self) -> bool:
    """
    Checks whether the current async request is finished or not

    Returns:
        bool: _description_
    """

@abstractmethod
def task_failed(self) -> bool:
    """
    Checks whether the current async request failed or not

    Returns:
        bool: _description_
    """

@abstractmethod
def task_timeout(self) -> bool:
    """
    Checks whether the current async request has timed out

    Returns:
        bool: _description_
    """

@abstractmethod
def poll(self, timeout_seconds: int, progress_callback: Callable[[ArkAsyncTask, int, ArkAsyncStatus], None]) -> bool:
    """
    Polls for the async request until it is finished
    Progress callbacks may also be used to be notified whats the async request status

    Args:
        timeout_seconds (int): _description_
        progress_callback (Callable[[ArkAsyncTask, int, ArkAsyncStatus], None]): _description_

    Returns:
        bool: _description_
    """
```

A user can then use the returned request, to poll or check whether a request is finished or not

Each of the existing services that have async requests, already have their respective requests implemented

The requests which are async, receive an ArkPollableModel type of request model, which also has information to whether to poll the request or not, and for how long to wait until timeout

Another feature of the pollable model, is if the authentication is refreshable, will also refresh it automatically during the polling operations if allowed and possible

## Predefined Pollers
There are pre defined pollers that can already be used, and are located in [ark_pollers.py](https://github.com/cyberark/ark-sdk-python/blob/master/ark_sdk_python/common/ark_pollers.py){:target="_blank" rel="noopener"}

Existing pollers are:

- default_poller - Default console logger polling
- line_spinner_poller
- pixel_spinner_poller
- moon_spinner_poller
- spinner_poller
- pie_spinner_poller

## Using the requests
In order to use the async requests, one can implement at as follows

```python
isp_auth = ArkISPAuth()
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username=username, auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
    ),
    secret=ArkSecret(secret='CoolPassword'),
)
dpa_service = ArkDPAAPI(isp_auth)
...
```
