from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.pcloud.applications.ark_pcloud_application_auth_method import ArkPCloudApplicationAuthMethodType


class ArkPCloudApplicationAuthMethodsFilter(ArkModel):
    app_id: str = Field(description='App id to filter on')
    auth_types: Optional[List[ArkPCloudApplicationAuthMethodType]] = Field(default=None, description='Auth types to filter with')
