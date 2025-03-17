from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudApplicationsFilter(ArkModel):
    location: Optional[str] = Field(default=None, description='Filter by location of the app')
    only_enabled: Optional[bool] = Field(default=None, description='Filter only enabled apps')
    business_owner_name: Optional[str] = Field(default=None, description='Filter by name, first or last')
    business_owner_email: Optional[str] = Field(default=None, description='Filter by email')
