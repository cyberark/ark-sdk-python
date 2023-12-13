from typing import List, Optional

from pydantic import Field, SecretStr, root_validator

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag


class ArkDPADBUpdateSecret(ArkModel):
    secret_id: Optional[str] = Field(description='Secret id to update')
    secret_name: Optional[str] = Field(description='Name of the secret to update')
    new_secret_name: Optional[str] = Field(description='New secret name to update to')
    description: Optional[str] = Field(description='Description about the secret to update')
    purpose: Optional[str] = Field(description='Purpose of the secret to update')
    tags: Optional[List[ArkDPADBTag]] = Field(description='Tags of the secret to change to')

    # Username Password Secret Type
    username: Optional[str] = Field(description='Name or id of the user for username_password type')
    password: Optional[SecretStr] = Field(description='Password of the user for username_password type')

    # PAM Account Secret Type
    pam_safe: Optional[str] = Field(description='Safe of the account for pam_account type')
    pam_account_name: Optional[str] = Field(description='Account name for pam_account type')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}

    # pylint: disable=no-self-use,no-self-argument
    @root_validator
    def validate_either(cls, values):
        if 'secret_id' not in values and 'secret_name' not in values:
            raise ValueError('Either secret id or secret name needs to be provided')
        return values
