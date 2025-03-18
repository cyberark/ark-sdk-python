import pprint

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret, IdentityArkAuthMethodSettings
from ark_sdk_python.services.pcloud.accounts import ArkPCloudAccountsService

if __name__ == '__main__':
    isp_auth = ArkISPAuth(cache_authentication=False)
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username='user@cyberark.cloud.12345',
            auth_method=ArkAuthMethod.Identity,
            auth_method_settings=IdentityArkAuthMethodSettings(),
        ),
        secret=ArkSecret(secret="CoolPassword"),
    )
    accounts_service = ArkPCloudAccountsService(isp_auth=isp_auth)
    for page in accounts_service.list_accounts():
        for item in page:
            pprint.pprint(item.model_dump())
