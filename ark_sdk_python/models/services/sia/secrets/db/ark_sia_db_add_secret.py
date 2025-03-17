from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel, ArkSecretStr
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_secret_type import ArkSIADBSecretType
from ark_sdk_python.models.services.sia.secrets.db.ark_sia_db_store_type import ArkSIADBStoreType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_tag import ArkSIADBTag


class ArkSIADBAddSecret(ArkModel):
    secret_name: str = Field(description='Name of the secret')
    description: str = Field(description='Description about the secret', default='')
    purpose: str = Field(description='Purpose of the secret', default='')
    secret_type: ArkSIADBSecretType = Field(description='Type of the secret')
    store_type: Optional[ArkSIADBStoreType] = Field(
        default=None, description='Store type of the secret of the secret, will be deduced by the secret type if not given'
    )
    tags: List[ArkSIADBTag] = Field(description='Tags of the secret', default_factory=list)

    # Username Password Secret Type
    username: Optional[str] = Field(default=None, description='Name or id of the user for username_password type')
    password: Optional[ArkSecretStr] = Field(default=None, description='Password of the user for username_password type')

    # PAM Account Secret Type
    pam_safe: Optional[str] = Field(default=None, description='Safe of the account for pam_account type')
    pam_account_name: Optional[str] = Field(default=None, description='Account name for pam_account type')

    # IAM Secret Type
    iam_account: Optional[str] = Field(default=None, description='Account number of the iam user')
    iam_username: Optional[str] = Field(default=None, description='Username portion in the ARN of the iam user')
    iam_access_key_id: Optional[ArkSecretStr] = Field(default=None, description='Access key id of the user')
    iam_secret_access_key: Optional[ArkSecretStr] = Field(default=None, description='Secret access key of the user')

    # Atlas Secret Type
    atlas_public_key: Optional[str] = Field(default=None, description='Public part of mongo atlas access keys')
    atlas_private_key: Optional[ArkSecretStr] = Field(default=None, description='Private part of mongo atlas access keys')
