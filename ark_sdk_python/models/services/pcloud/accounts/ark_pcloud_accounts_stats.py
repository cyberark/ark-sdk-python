from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudAccountsStats(ArkModel):
    accounts_count: int = Field(description='Overall accounts count')
    accounts_count_by_platform_id: Dict[str, int] = Field(description='Accounts count by platform id')
    accounts_count_by_safe_name: Dict[str, int] = Field(description='Accounts count by safe name')
