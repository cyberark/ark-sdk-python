# pylint: disable=invalid-name
from enum import Enum
from typing import Dict, Final

from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_secret_type import ArkDPADBSecretType


class ArkDPADBStoreType(str, Enum):
    Managed = 'managed'
    PAM = 'pam'


SECRET_TYPE_TO_STORE_DICT: Final[Dict[ArkDPADBSecretType, ArkDPADBStoreType]] = {
    ArkDPADBSecretType.UsernamePassword: ArkDPADBStoreType.Managed,
    ArkDPADBSecretType.CyberArkPAM: ArkDPADBStoreType.PAM,
}
