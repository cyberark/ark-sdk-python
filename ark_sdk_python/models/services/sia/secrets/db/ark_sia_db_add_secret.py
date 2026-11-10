from typing import Annotated, List, Optional

from pydantic import Field, StringConstraints

from ark_sdk_python.models.ark_model import ArkCamelizedModel, ArkModel, ArkSecretStr
from ark_sdk_python.models.common import ArkRegion
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


class ArkSIADBAddStrongAccount(ArkCamelizedModel):
    store_type: str = Field(description='Store type of the account (managed,pam)')
    name: str = Field(description='Name of the account')

    # Used in case the StoreType is pam
    safe: Optional[str] = Field(default=None, description='Safe of the account')
    account_name: Optional[str] = Field(default=None, description='Account name of the account')

    # AccountProperties Fields
    platform: Optional[str] = Field(
        default=None, description='Platform of the account, The required Properties are dependent on the platform'
    )
    address: Optional[str] = Field(default=None, description='Address of the account')
    username: Optional[str] = Field(default=None, description='Username of the account')
    port: Optional[int] = Field(default=None, description='Port of the account')
    database: Optional[str] = Field(default=None, description='Database of the account')
    dsn: Optional[Annotated[str, StringConstraints(max_length=255)]] = Field(
        default=None, description='Data Source Name (DSN) connection string (PostgreSQL, MySQL, MariaDB, MSSql, Oracle, MongoDB)'
    )

    aws_access_key_id: Optional[str] = Field(default=None, description='AWS Access Key ID of the account')
    aws_account_id: Optional[str] = Field(default=None, description='AWS Account ID of the account')
    aws_account_alias_name: Optional[Annotated[str, StringConstraints(max_length=255)]] = Field(
        default=None, description='AWS account alias name (AWSAccessKeys)'
    )
    region: Optional[ArkRegion] = Field(default=None, description='AWS region (AWSAccessKeys)')
    auth_database: Optional[str] = Field(default=None, description='Authentication database of the account (MongoDB)')

    # WinDomain specific fields
    log_on_to: Optional[Annotated[str, StringConstraints(max_length=255)]] = Field(default=None, description='Log on to field (WinDomain)')
    user_dn: Optional[Annotated[str, StringConstraints(max_length=255)]] = Field(
        default=None, alias='userDN', description='User DN field (WinDomain)'
    )

    # MongoDB specific fields
    replica_set: Optional[Annotated[str, StringConstraints(max_length=255)]] = Field(
        default=None, description='Replica set of the account (MongoDB)'
    )
    use_ssl: Optional[Annotated[str, StringConstraints(max_length=255)]] = Field(
        default=None, description='SSL configuration for the account (MongoDB)'
    )

    # MSSql specific fields
    reconcile_is_win_account: Optional[bool] = Field(default=None, description='Whether to reconcile as Windows account (MSSql)')

    # PasswordSecretObject Fields
    password: Optional[ArkSecretStr] = Field(default=None, description='Password of the account')
    secret_access_key: Optional[ArkSecretStr] = Field(default=None, description='Secret access key of the account')
