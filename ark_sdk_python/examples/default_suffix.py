from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.ark_profile import ArkProfileLoader
from ark_sdk_python.models.services.identity.directories import ArkIdentityListDirectoriesEntities
from ark_sdk_python.services.identity import ArkIdentityAPI

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(ArkProfileLoader().load_default_profile())
    identity_api = ArkIdentityAPI(isp_auth)
    print(identity_api.identity_directories.tenant_default_suffix())
    for page in identity_api.identity_directories.list_directories_entities(ArkIdentityListDirectoriesEntities()):
        print([i.name for i in page.items])
