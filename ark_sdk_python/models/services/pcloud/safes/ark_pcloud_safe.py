from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel, ArkModel


class ArkPCloudSafeCreator(ArkModel):
    id: str = Field(description='ID of the safe creator')
    name: str = Field(description='Name of the safe creator')


class ArkPCloudBaseSafe(ArkCamelizedModel):
    safe_name: Optional[str] = Field(description='Name of the safe', default=None)
    description: Optional[str] = Field(description='Description about the safe', default=None)
    location: Optional[str] = Field(description='Location of the safe in the vault', default="\\")
    number_of_days_retention: Optional[int] = Field(description='Number of retention days on the safe objects', default=0)
    number_of_versions_retention: Optional[int] = Field(description='Number of retention versions on the safe objects', default=None)
    auto_purge_enabled: Optional[bool] = Field(description='Whether auto purge is enabled on the safe', default=False)
    olac_enabled: Optional[bool] = Field(description='Whether object level access control is enabled', default=False)
    managing_cpm: Optional[str] = Field(description='Managing CPM of the safe', default=None)


class ArkPCloudSafe(ArkPCloudBaseSafe):
    creator: Optional[ArkPCloudSafeCreator] = Field(description='Creator of the safe', default=None)
    creation_time: Optional[int] = Field(description='Creation time of the safe', default=None)
    last_modification_time: Optional[int] = Field(description='Last time the safe was modified', default=None)
    safe_id: str = Field(description='Safe url to access with as an id', alias='safeUrlId')
    safe_number: Optional[int] = Field(description='ID number of the safe', default=None)
    is_expired_member: Optional[bool] = Field(description='Whether any member is expired', default=None)
