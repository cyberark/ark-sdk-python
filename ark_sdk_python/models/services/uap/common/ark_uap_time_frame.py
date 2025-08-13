from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.ark_model import ArkSerializableDatetime


class ArkUAPTimeFrame(ArkCamelizedModel):
    from_time: Optional[ArkSerializableDatetime] = Field(default=None, description='Time from which the policy is effective')
    to_time: Optional[ArkSerializableDatetime] = Field(default=None, description='Time to which the policy is expired')

    @field_validator('from_time', 'to_time', mode='before')
    @classmethod
    def validate_datetime_format(cls, value):
        if value is None:
            return value
        if isinstance(value, datetime):
            return value
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        except ValueError as exc:
            raise ValueError("Datetime must be in format 'yyyy-MM-ddTHH:mm:ss'") from exc
