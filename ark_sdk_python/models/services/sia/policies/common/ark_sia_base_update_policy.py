from typing import Optional

from pydantic import Field, model_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_rule_status import ArkSIARuleStatus


class ArkSIABaseUpdatePolicy(ArkCamelizedModel):
    policy_id: Optional[str] = Field(default=None, description='Policy id to update')
    policy_name: Optional[str] = Field(default=None, description='Policy name to update')
    new_policy_name: Optional[str] = Field(default=None, description='New policy name to update')
    description: Optional[str] = Field(default=None, description='Description about the policy to be updated')
    status: Optional[ArkSIARuleStatus] = Field(default=None, description='Status of the policy to update')
    start_date: Optional[str] = Field(default=None, description='New start time to update')
    end_date: Optional[str] = Field(default=None, description='New end time to update')

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='before')
    @classmethod
    def validate_either(cls, values):
        if 'policy_id' not in values and 'policy_name' not in values:
            raise ValueError('Either policy id or policy name needs to be provided')
        return values
