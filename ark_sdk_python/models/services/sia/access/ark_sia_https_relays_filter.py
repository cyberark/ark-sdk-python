from typing import List, Literal, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAHttpsRelaysFilter(ArkModel):
    only_latest_version_relays: Optional[bool] = Field(default=None, description='Filter only relays running the latest version')
    only_relays_with_sessions: Optional[bool] = Field(default=None, description='Filter only relays with active sessions')
    status_codes: Optional[List[Literal['INACTIVE', 'ACTIVE', 'DOWNLOADED']]] = Field(
        default=None, description='Filter by list of status codes'
    )
