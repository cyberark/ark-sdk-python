from typing import Dict, List

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.pcloud.applications.ark_pcloud_application_auth_method import ArkPCloudApplicationAuthMethodType


class ArkPCloudAppicationsStats(ArkModel):
    count: int = Field(description='Overall application count')
    disabled_apps: List[str] = Field(description='Disabled applications')
    auth_types_count: Dict[ArkPCloudApplicationAuthMethodType, int] = Field(description='Auth types count for all applications')
    applications_auth_method_types: Dict[str, List[ArkPCloudApplicationAuthMethodType]] = Field(
        description='Applicastions auth methods types'
    )
