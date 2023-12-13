from typing import Dict, Optional

from ark_sdk_python.models.ark_profile import ArkProfile
from ark_sdk_python.models.auth.ark_auth_method import ArkAuthMethod, ArkAuthMethodSettingsMap
from ark_sdk_python.models.auth.ark_auth_profile import ArkAuthProfile


def generate_profile_for(auth_name: str, auth_method: ArkAuthMethod, settings: Optional[Dict] = None) -> ArkProfile:
    return ArkProfile(auth_profiles={auth_name: generate_auth_profile_for(auth_method, settings)})


def generate_auth_profile_for(auth_method: ArkAuthMethod, settings: Optional[Dict] = None) -> ArkAuthProfile:
    settings = settings or {}
    return ArkAuthProfile(
        username='user@user.com', auth_method=auth_method, auth_method_settings=ArkAuthMethodSettingsMap[auth_method](**settings)
    )
