---
title: Pagination
description: Pagination
---

# Pagination

When a response returns many items or is paginated, the response contains an page iterator instead of all the items. This ensures fast response times and the ability to just retrieve a required subset of items.

Responses that do return paginated results contain an item iterator.

An example of such API is the list accounts:
```python
def list_accounts(self) -> Iterator[ArkPCloudAccountsPage]:
```

Where the list accounts returns an iterator of accounts pages

This can later be used like any other python iterator in the following fashion

```python
isp_auth = ArkISPAuth(cache_authentication=False)
isp_auth.authenticate(
    auth_profile=ArkAuthProfile(
        username='smarom@cyberark.cloud.84573',
        auth_method=ArkAuthMethod.Identity,
        auth_method_settings=IdentityArkAuthMethodSettings(),
    ),
    secret=ArkSecret(secret="CoolPassword"),
)
accounts_service = ArkPCloudAccountsService(isp_auth=isp_auth)
for page in accounts_service.list_accounts():
    for item in page:
        pprint.pprint(item.model_dump())
```

Where we list the account pages and for each page for each item we print it
