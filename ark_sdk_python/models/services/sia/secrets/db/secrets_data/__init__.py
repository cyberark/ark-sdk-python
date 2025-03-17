from typing import Union

from ark_sdk_python.models.services.sia.secrets.db.secrets_data.ark_sia_db_atlas_access_keys_secret_data import (
    ArkSIADBAtlasAccessKeysSecretData,
    ArkSIADBExposedAtlasAccessKeysSecretData,
)
from ark_sdk_python.models.services.sia.secrets.db.secrets_data.ark_sia_db_iam_user_secret_data import (
    ArkSIADBExposedIAMUserSecretData,
    ArkSIADBIAMUserSecretData,
)
from ark_sdk_python.models.services.sia.secrets.db.secrets_data.ark_sia_db_user_password_secret_data import (
    ArkSIADBExposedUserPasswordSecretData,
    ArkSIADBUserPasswordSecretData,
)

ArkSIADBSecretDataTypes = Union[ArkSIADBUserPasswordSecretData, ArkSIADBIAMUserSecretData, ArkSIADBAtlasAccessKeysSecretData]
ArkSIADBSecretExposedDataTypes = Union[
    ArkSIADBExposedUserPasswordSecretData, ArkSIADBExposedIAMUserSecretData, ArkSIADBExposedAtlasAccessKeysSecretData
]
