---
title: Async requests
description: Async Requests
---

# Async requests

To support async requests, relevant methods return an ArkAsyncRequest type with the following interfaces:

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

You can call these methods for polling the service to check the request's status.

Async requests also inherits the ArkPollableModel type, which contains information about whether or not to poll the request and how long to wait until the request times out. Additionally, when the request's authenticator can be refreshed, it is refreshed during the polling cycle.

## Predefined pollers

These predefined pollers can be used (see [ark_pollers.py](https://github.com/cyberark/ark-sdk-python/blob/main/ark_sdk_python/common/ark_pollers.py){:target="_blank" rel="noopener"}):

- default_poller (default console logger polling)
- line_spinner_poller
- pixel_spinner_poller
- moon_spinner_poller
- spinner_poller
- pie_spinner_poller
