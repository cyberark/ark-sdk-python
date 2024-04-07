import json
from enum import Enum
from json.encoder import JSONEncoder
from typing import Dict, List, Optional

from pydantic import Field, conlist

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.common.identity.ark_identity_common_schemas import IdentityApiResponse


class DirectoryService(str, Enum):
    AD = 'AdProxy'  # groups
    Identity = 'CDS'  # roles
    FDS = 'FDS'


class DirectoryServiceMetadata(ArkModel):
    service: str = Field(alias='Service')
    directory_service_uuid: str = Field(alias='directoryServiceUuid')


class DirectoryServiceRow(ArkModel):
    row: DirectoryServiceMetadata = Field(alias='Row')


class GetDirectorySevicesResult(ArkModel):
    results: conlist(DirectoryServiceRow, min_items=1) = Field(alias='Results')


class GetDirectoryServicesResponse(IdentityApiResponse):
    result: GetDirectorySevicesResult = Field(alias='Result')


class DirectorySearchArgs(ArkModel):
    page_number: int = Field(default=1, alias='PageNumber')
    page_size: int = Field(default=100000, alias='PageSize')
    limit: int = Field(default=100000, alias='Limit')
    sort_by: str = Field(default='', alias='SortBy')
    caching: int = Field(default=-1, alias='Caching')
    dir: str = Field(default='', alias='Direction')
    ascending: bool = Field(default=True, alias='Ascending')


class DirectoryServiceQueryRequest(ArkModel):
    directory_services: List = Field(alias='directoryServices')
    group: str = Field(default='{}')
    roles: str = Field(default='{}')
    user: str = Field(default='{}')
    args: DirectorySearchArgs = Field(alias='Args')

    def __init__(self, search_string: str = None, **data):
        super().__init__(**data)
        if search_string:
            group_filter_dict: Dict = {"_or": [{"DisplayName": {"_like": search_string}}, {"SystemName": {"_like": search_string}}]}
            self.group = json.dumps(group_filter_dict)
            roles_filter_dict: Dict = {"Name": {"_like": {"value": search_string, "ignoreCase": True}}}
            self.roles = json.dumps(roles_filter_dict)
            users_filter_dict: Dict = {'DisplayName': {'_like': search_string}}
            self.user = json.dumps(users_filter_dict)


class DirectoryServiceQuerySpecificRoleRequest(DirectoryServiceQueryRequest):
    def __init__(self, role_name: str = None, **data):
        super().__init__(**data)
        if role_name:
            self.roles = str({'Name': {'_eq': role_name}})


class GroupRow(ArkModel):
    display_name: Optional[str] = Field(alias='DisplayName')
    service_instance_localized: str = Field(alias='ServiceInstanceLocalized')
    directory_service_type: DirectoryService = Field(alias='ServiceType')
    system_name: Optional[str] = Field(alias='SystemName')
    internal_id: Optional[str] = Field(alias='InternalName')


class GroupResult(ArkModel):
    row: GroupRow = Field(alias='Row')


class GroupsResult(ArkModel):
    results: List[GroupResult] = Field(alias='Results')
    full_count: Optional[int] = Field(alias='FullCount')


class RoleAdminRight(ArkModel):
    path: str = Field(alias='Path')
    service_name: Optional[str] = Field(alias='ServiceName')


class RoleRow(ArkModel):
    name: Optional[str] = Field(alias='Name')
    id: str = Field(alias='_ID')
    admin_rights: Optional[List[RoleAdminRight]] = Field(alias='AdministrativeRights')
    is_hidden: Optional[bool] = Field(alias='IsHidden')
    description: Optional[str] = Field(alias='Description')


class RoleResult(ArkModel):
    row: RoleRow = Field(alias='Row')


class RolesResult(ArkModel):
    results: List[RoleResult] = Field(alias='Results')
    full_count: Optional[int] = Field(alias='FullCount')


class UserRow(ArkModel):
    display_name: Optional[str] = Field(alias='DisplayName')
    service_instance_localized: str = Field(alias='ServiceInstanceLocalized')
    distinguished_name: str = Field(alias='DistinguishedName')
    system_name: Optional[str] = Field(alias='SystemName')
    directory_service_type: DirectoryService = Field(alias='ServiceType')
    email: Optional[str] = Field(alias='EMail')
    internal_id: Optional[str] = Field(alias='InternalName')
    description: Optional[str] = Field(alias='Description')


class UserResult(ArkModel):
    row: UserRow = Field(alias='Row')


class UsersResult(ArkModel):
    results: List[UserResult] = Field(alias='Results')
    full_count: Optional[int] = Field(alias='FullCount')


class QueryResult(ArkModel):
    groups: Optional[GroupsResult] = Field(alias='Group')
    roles: Optional[RolesResult] = Field()
    users: Optional[UsersResult] = Field(alias='User')


class DirectoryServiceQueryResponse(IdentityApiResponse):
    result: QueryResult = Field(alias='Result')


class DirectorySearchEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
