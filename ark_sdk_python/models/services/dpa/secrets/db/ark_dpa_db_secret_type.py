# pylint: disable=invalid-name
from enum import Enum


class ArkDPADBSecretType(str, Enum):
    UsernamePassword = 'username_password'
    IAMUser = 'iam_user'
    CyberArkPAM = 'cyberark_pam'
