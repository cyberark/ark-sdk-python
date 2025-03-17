from typing import List, Optional

from pydantic import Field, model_validator

from ark_sdk_python.models.ark_model import ArkModel, ArkSecretStr
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_tag import ArkSIADBTag


class ArkSIADBUpdateSecret(ArkModel):
    secret_id: Optional[str] = Field(default=None, description='Secret id to update')
    secret_name: Optional[str] = Field(default=None, description='Name of the secret to update')
    new_secret_name: Optional[str] = Field(default=None, description='New secret name to update to')
    description: Optional[str] = Field(default=None, description='Description about the secret to update')
    purpose: Optional[str] = Field(default=None, description='Purpose of the secret to update')
    tags: Optional[List[ArkSIADBTag]] = Field(default=None, description='Tags of the secret to change to')

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

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='before')
    @classmethod
    def validate_either(cls, values):
        if 'secret_id' not in values and 'secret_name' not in values:
            raise ValueError('Either secret id or secret name needs to be provided')
        return values
