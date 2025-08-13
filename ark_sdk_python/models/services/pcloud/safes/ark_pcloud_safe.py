from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel, ArkModel


class ArkPCloudSafeCreator(ArkModel):
    id: str = Field(description='ID of the safe creator')
    name: str = Field(description='Name of the safe creator')


class ArkPCloudBaseSafe(ArkCamelizedModel):
    safe_name: Optional[str] = Field(default=None, description='Name of the safe')
    description: Optional[str] = Field(default=None, description='Description about the safe')
    location: Optional[str] = Field(description='Location of the safe in the vault', default="\\")
    number_of_days_retention: Optional[int] = Field(description='Number of retention days on the safe objects', default=0)
    number_of_versions_retention: Optional[int] = Field(default=None, description='Number of retention versions on the safe objects')
    auto_purge_enabled: Optional[bool] = Field(description='Whether auto purge is enabled on the safe', default=False)
    olac_enabled: Optional[bool] = Field(description='Whether object level access control is enabled', default=False)
    managing_cpm: Optional[str] = Field(default=None, description='Managing CPM of the safe')


class ArkPCloudSafe(ArkPCloudBaseSafe):
    creator: Optional[ArkPCloudSafeCreator] = Field(default=None, description='Creator of the safe')
    creation_time: Optional[int] = Field(default=None, description='Creation time of the safe')
    last_modification_time: Optional[int] = Field(default=None, description='Last time the safe was modified')
    safe_id: str = Field(description='Safe url to access with as an id', alias='safeUrlId')
    safe_number: Optional[int] = Field(default=None, description='ID number of the safe')
    is_expired_member: Optional[bool] = Field(default=None, description='Whether any member is expired')
