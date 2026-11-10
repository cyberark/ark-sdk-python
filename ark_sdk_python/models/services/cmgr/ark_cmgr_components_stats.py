from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkCountedValues
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import ArkCmgrComponentStatusCode


class ArkCmgrComponentsStats(ArkModel):
    components_count: int = Field(description='Overall components count')
    components_per_connector: Dict[str, ArkCountedValues] = Field(description='Components count and values per connector')
    components_count_per_status: Dict[ArkCmgrComponentStatusCode, int] = Field(description='Components count by status code')
    maintenanced_components: ArkCountedValues = Field(description='Maintenanced components count and values')
    upgradable_components: ArkCountedValues = Field(description='Upgradable components count and values')
