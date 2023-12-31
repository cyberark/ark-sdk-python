import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field, validator

from ark_sdk_python.common.ark_logger import get_logger
from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.auth.ark_auth_method import ArkAuthMethodSettingsMap
from ark_sdk_python.models.auth.ark_auth_profile import ArkAuthProfile


class ArkProfile(ArkModel):
    profile_name: str = Field(default='ark', alias='Profile Name', description='Profile name for storage')
    profile_description: str = Field(default='Default Ark Profile', alias='Profile Description', description='Info about the profile')
    auth_profiles: Dict[str, ArkAuthProfile] = Field(
        description='Authentication profiles configurations, map from name of the authenticator to its profile', default_factory=dict
    )

    # pylint: disable=no-self-use,no-self-argument
    @validator('auth_profiles', pre=True)
    def validate_auth_profiles(cls, val):
        auth_profiles = {}
        for k, v in val.items():
            auth_profile = ArkAuthProfile.parse_obj(v)
            # Make sure that the settings are parsed with the correct class
            # Due to properties overlapping
            if 'auth_method_settings' in v:
                auth_profile.auth_method_settings = ArkAuthMethodSettingsMap[auth_profile.auth_method].parse_obj(v['auth_method_settings'])
            auth_profiles[k] = auth_profile
        return auth_profiles


class ArkProfileLoader:
    @staticmethod
    def profiles_folder() -> str:
        """
        Retrieves the profiles folder pathname, from the environment variable when set; otherwise, from the default location.

        Returns:
            str: _description_
        """
        return os.getenv('ARK_PROFILES_FOLDER', os.path.join(Path.home(), '.ark_profiles'))

    @staticmethod
    def default_profile_name() -> str:
        """
        Getter for the default profile name.

        Returns:
            str: _description_
        """
        return 'ark'

    @staticmethod
    def deduce_profile_name(profile_name: Optional[str] = None) -> str:
        """
        Deduces the profile name from the env.

        Args:
            profile_name (Optional[str], optional): Defaults to `None`

        Returns:
            str: _description_
        """
        if profile_name and profile_name != ArkProfileLoader.default_profile_name():
            return profile_name
        if 'ARK_PROFILE' in os.environ:
            return os.environ['ARK_PROFILE']
        if profile_name:
            return profile_name
        return ArkProfileLoader.default_profile_name()

    @staticmethod
    def load_default_profile() -> ArkProfile:
        """
        Loads the default profile, either from the OS or creates a new one.

        Returns:
            ArkProfile: _description_
        """
        folder = ArkProfileLoader.profiles_folder()
        profile_name = ArkProfileLoader.deduce_profile_name()
        if os.path.exists(os.path.join(folder, profile_name)):
            profile: ArkProfile = ArkProfile.parse_file(os.path.join(folder, profile_name))
            return profile
        return ArkProfile()

    @staticmethod
    def load_profile(profile_name: str) -> Optional[ArkProfile]:
        """
        Loads the specified profile from the OS.
        Returns `None` when a profile is not found with the specified name.

        Args:
            profile_name (str): _description_

        Returns:
            Optional[ArkProfile]: _description_
        """
        folder = ArkProfileLoader.profiles_folder()
        if os.path.exists(os.path.join(folder, profile_name)):
            profile: ArkProfile = ArkProfile.parse_file(os.path.join(folder, profile_name))
            return profile
        return None

    @staticmethod
    def save_profile(profile: ArkProfile) -> None:
        """
        Saves the profile to the profiles folder on the filesystem.

        Args:
            profile (ArkProfile): _description_
        """
        folder = ArkProfileLoader.profiles_folder()
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, profile.profile_name), 'w', encoding='utf-8') as f:
            f.write(profile.json(indent=4, by_alias=False))

    @staticmethod
    def load_all_profiles() -> Optional[List[ArkProfile]]:
        """
        Loads all the profiles that exist on the machine.

        Returns:
            Optional[List[ArkProfile]]: _description_
        """
        logger = get_logger('load_all_profiles')
        folder = ArkProfileLoader.profiles_folder()
        if not os.path.exists(folder):
            return None
        profiles: List[ArkProfile] = []
        for profile_name in os.listdir(folder):
            try:
                profiles.append(ArkProfile.parse_file(os.path.join(folder, profile_name)))
            except Exception as ex:
                logger.warning(f'Profile {profile_name} failed to be loaded successfully [{str(ex)}]')
                continue
        return profiles

    @staticmethod
    def delete_profile(profile_name: str) -> None:
        """
        Deletes the specified profile.

        Args:
            profile_name (str): The name of the profile to delete
        """
        folder = ArkProfileLoader.profiles_folder()
        if not os.path.exists(folder):
            return None
        if os.path.exists(os.path.join(folder, profile_name)):
            os.unlink(os.path.join(folder, profile_name))

    @staticmethod
    def clear_all_profiles() -> None:
        """
        Clears all profiles.
        """
        folder = ArkProfileLoader.profiles_folder()
        if not os.path.exists(folder):
            return None
        for profile_name in os.listdir(folder):
            os.unlink(os.path.join(folder, profile_name))

    @staticmethod
    def profile_exists(profile_name: str) -> bool:
        """
        Checks if the specified profile exists.

        Args:
            profile_name (str): _description_

        Returns:
            bool: _description_
        """
        folder = ArkProfileLoader.profiles_folder()
        if not os.path.exists(folder):
            return False
        return os.path.exists(os.path.join(folder, profile_name))
