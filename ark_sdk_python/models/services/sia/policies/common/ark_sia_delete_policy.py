from typing import Optional

from pydantic import Field, model_validator

from ark_sdk_python.models import ArkModel


class ArkSIADeletePolicy(ArkModel):
    policy_id: Optional[str] = Field(default=None, description='Policy id to delete')
    policy_name: Optional[str] = Field(default=None, description='Policy name to delete')

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='before')
    @classmethod
    def validate_either(cls, values):
        if 'policy_id' not in values and 'policy_name' not in values:
            raise ValueError('Either policy id or policy name needs to be provided')
        return values
