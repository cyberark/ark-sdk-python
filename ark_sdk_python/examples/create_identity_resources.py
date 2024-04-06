from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.auth import ArkAuthMethod, ArkAuthProfile, ArkSecret, IdentityArkAuthMethodSettings
from ark_sdk_python.models.services.identity.roles import ArkIdentityCreateRole
from ark_sdk_python.models.services.identity.users import ArkIdentityCreateUser
from ark_sdk_python.services.identity import ArkIdentityAPI

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username='CoolUser', auth_method=ArkAuthMethod.Identity, auth_method_settings=IdentityArkAuthMethodSettings()
        ),
        secret=ArkSecret(secret='CoolPassword'),
    )

    # Create an identity service to create some users and roles
    print('Creating identity roles and users')
    identity_api = ArkIdentityAPI(isp_auth)
    identity_api.identity_roles.create_role(ArkIdentityCreateRole(role_name='IT'))
    identity_api.identity_users.create_user(ArkIdentityCreateUser(username='it_user', password='CoolPassword', roles=['IT']))
