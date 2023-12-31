# pylint: disable=invalid-name
from enum import Enum


class ArkDPADBSecretType(str, Enum):
    UsernamePassword = 'username_password'
    CyberArkPAM = 'cyberark_pam'
