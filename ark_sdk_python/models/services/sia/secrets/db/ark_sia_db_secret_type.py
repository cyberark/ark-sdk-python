# pylint: disable=invalid-name
from enum import Enum


class ArkSIADBSecretType(str, Enum):
    UsernamePassword = 'username_password'
    IAMUser = 'iam_user'
    CyberArkPAM = 'cyberark_pam'
    AtlasAccessKeys = 'atlas_access_keys'
