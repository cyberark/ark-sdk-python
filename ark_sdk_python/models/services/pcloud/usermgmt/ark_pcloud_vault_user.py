from enum import Enum
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudVaultAuthMethod(str, Enum):
    CyberArk = 'CyberArk'
    LDAP = 'LDAP'
    Radius = 'RADIUS'
    AuthTypePass = 'AuthTypePass'


class ArkPCloudVaultAuthorization(str, Enum):
    AddSafes = 'AddSafes'
    AuditUsers = 'AuditUsers'
    AddUpdateUsers = 'AddUpdateUsers'
    ResetUsersPasswords = 'ResetUsersPasswords'
    ActivateUsers = 'ActivateUsers'
    AddNetworkAreas = 'AddNetworkAreas'
    ManageDirectoryMapping = 'ManageDirectoryMapping'
    ManageServerFileCategories = 'ManageServerFileCategories'
    BackupAllSafes = 'BackupAllSafes'
    RestoreAllSafes = 'RestoreAllSafes'


class ArkPCloudVaultBusinessAddress(ArkCamelizedModel):
    work_street: Optional[str] = Field(default=None, description='Work street')
    work_city: Optional[str] = Field(default=None, description='Work city')
    work_state: Optional[str] = Field(default=None, description='Work state')
    work_zip: Optional[str] = Field(default=None, description='Work zip')
    work_country: Optional[str] = Field(default=None, description='Work country')


class ArkPCloudVaultUserInternet(ArkCamelizedModel):
    home_page: Optional[str] = Field(default=None, description='Home page')
    home_email: Optional[str] = Field(default=None, description='Home email')
    business_email: Optional[str] = Field(default=None, description='Business email')
    other_email: Optional[str] = Field(default=None, description='Other email')


class ArkPCloudVaultUserPhones(ArkCamelizedModel):
    home_number: Optional[str] = Field(default=None, description='Home number')
    business_number: Optional[str] = Field(default=None, description='Business number')
    cellular_number: Optional[str] = Field(default=None, description='Cellular number')
    fax_number: Optional[str] = Field(default=None, description='Fax number')
    pager_number: Optional[str] = Field(default=None, description='Pager number')


class ArkPCloudVaultUserPersonalDetails(ArkCamelizedModel):
    street: Optional[str] = Field(default=None, description='Street')
    city: Optional[str] = Field(default=None, description='City')
    state: Optional[str] = Field(default=None, description='State')
    zip: Optional[str] = Field(default=None, description='Zip')
    country: Optional[str] = Field(default=None, description='Country')
    title: Optional[str] = Field(default=None, description='Title of the user')
    organization: Optional[str] = Field(default=None, description='Orgnaization')
    profession: Optional[str] = Field(default=None, description='Profession')
    first_name: Optional[str] = Field(default=None, description='First name')
    middle_name: Optional[str] = Field(default=None, description='Middle name')
    last_name: Optional[str] = Field(default=None, description='Last name')


class ArkPCloudBaseVaultUser(ArkCamelizedModel):
    username: Optional[str] = Field(default=None, description='Username defined for the user')
    user_type: Optional[str] = Field(description='Type of the user, for example EPVUser', default='EPVUser')
    location: Optional[str] = Field(description='Location of the user in the vault', default='\\')
    vault_authorizations: Optional[List[ArkPCloudVaultAuthorization]] = Field(
        default=None, description='List of authorizations for the user on the vault'
    )
    non_authorized_interfaces: Optional[List[str]] = Field(default=None, description='List of non authorized interfaces for the user')
    description: Optional[str] = Field(default=None, description='Description about the user')
    distinguished_name: Optional[str] = Field(default=None, description='Distinguished name of the user')
    business_address: Optional[ArkPCloudVaultBusinessAddress] = Field(default=None, description='Business address details of the user')
    internet: Optional[ArkPCloudVaultUserInternet] = Field(default=None, description='Internet details of the user')
    phones: Optional[ArkPCloudVaultUserPhones] = Field(default=None, description='Phone numbers of the user')
    personal_details: Optional[ArkPCloudVaultUserPersonalDetails] = Field(default=None, description='Personal details about the user')


class ArkPCloudVaultUserGroupMembership(ArkCamelizedModel):
    group_id: int = Field(description='ID of the group')
    group_name: str = Field(description='Name of the group')
    group_type: str = Field(description='Type of the group')


class ArkPCloudVaultUser(ArkPCloudBaseVaultUser):
    id: int = Field(description='ID of the user')
    source: str = Field(description='Source of where the user directory is')
    component_user: bool = Field(description='Whether the user is a component user or a personal one')
    authentication_method: Optional[List[ArkPCloudVaultAuthMethod]] = Field(default=None, description='Authentication method of the user')
    group_memberships: Optional[List[ArkPCloudVaultUserGroupMembership]] = Field(
        default=None, description='Memberships of the user in groups'
    )
    vault_authorization: List[str] = Field(description='Authorizations of the user to applications')
