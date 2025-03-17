# pylint: disable=invalid-name
from enum import Enum
from typing import Dict, Final

from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_secret_type import ArkSIADBSecretType


class ArkSIADBStoreType(str, Enum):
    Managed = 'managed'
    PAM = 'pam'


SECRET_TYPE_TO_STORE_DICT: Final[Dict[ArkSIADBSecretType, ArkSIADBStoreType]] = {
    ArkSIADBSecretType.UsernamePassword: ArkSIADBStoreType.Managed,
    ArkSIADBSecretType.CyberArkPAM: ArkSIADBStoreType.PAM,
    ArkSIADBSecretType.IAMUser: ArkSIADBStoreType.Managed,
    ArkSIADBSecretType.AtlasAccessKeys: ArkSIADBStoreType.Managed,
}
