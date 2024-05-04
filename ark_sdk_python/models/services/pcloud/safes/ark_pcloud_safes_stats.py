from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudSafesStats(ArkModel):
    safes_count: int = Field(description='Overall safes count')
    safes_count_by_location: Dict[str, int] = Field(description='Safes count by locations')
    safes_count_by_creator: Dict[str, int] = Field(description='Safes count by creator')
