from typing import List, Optional

from pydantic import Field, SecretStr

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_secret_type import ArkDPADBSecretType
from ark_sdk_python.models.services.dpa.secrets.db.ark_dpa_db_store_type import ArkDPADBStoreType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag


class ArkDPADBAddSecret(ArkModel):
    secret_name: str = Field(description='Name of the secret')
    description: str = Field(description='Description about the secret', default='')
    purpose: str = Field(description='Purpose of the secret', default='')
    secret_type: ArkDPADBSecretType = Field(description='Type of the secret')
    store_type: Optional[ArkDPADBStoreType] = Field(
        description='Store type of the secret of the secret, will be deduced by the secret type if not given'
    )
    tags: List[ArkDPADBTag] = Field(description='Tags of the secret', default_factory=list)

    # Username Password Secret Type
    username: Optional[str] = Field(description='Name or id of the user for username_password type')
    password: Optional[SecretStr] = Field(description='Password of the user for username_password type')

    # PAM Account Secret Type
    pam_safe: Optional[str] = Field(description='Safe of the account for pam_account type')
    pam_account_name: Optional[str] = Field(description='Account name for pam_account type')

    # IAM Secret Type
    iam_account: Optional[str] = Field(description='Account number of the iam user')
    iam_username: Optional[str] = Field(description='Username portion in the ARN of the iam user')
    iam_access_key_id: Optional[SecretStr] = Field(description='Access key id of the user')
    iam_secret_access_key: Optional[SecretStr] = Field(description='Secret access key of the user')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}
