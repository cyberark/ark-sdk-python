from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import Field, conint

from ark_sdk_python.models import ArkCamelizedModel


class ArkDPADaysOfWeek(str, Enum):
    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'


class ArkDPABaseConnectionInformation(ArkCamelizedModel):
    days_of_week: Optional[List[ArkDPADaysOfWeek]] = Field(
        description='Days of week this rule is allowed on', default=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    )
    full_days: Optional[bool] = Field(description='Whether this rule is allowed for the entirety of the week', default=False)
    hours_from: Optional[str] = Field(description='From which hours this rule is allowed')
    hours_to: Optional[str] = Field(description='To which hours this rule is allowed')
    time_zone: Optional[Union[Dict, str]] = Field(description='Timezone in which the hours apply to')
    grant_access: conint(gt=0, le=24) = Field(description='For how many hours to grant access in this rule in hours', default=2)
    idle_time: Optional[conint(gt=0, le=120)] = Field(
        description='How long the session can stay idle until stopped in minutes', default=None
    )
