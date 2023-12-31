from typing import Optional

from pydantic import Field, root_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_rule_status import ArkDPARuleStatus


class ArkDPABaseUpdatePolicy(ArkCamelizedModel):
    policy_id: Optional[str] = Field(description='Policy id to update')
    policy_name: Optional[str] = Field(description='Policy name to update')
    new_policy_name: Optional[str] = Field(description='New policy name to update')
    description: Optional[str] = Field(description='Description about the policy to be updated')
    status: Optional[ArkDPARuleStatus] = Field(description='Status of the policy to update')
    start_date: Optional[str] = Field(description='New start time to update')
    end_date: Optional[str] = Field(description='New end time to update')

    # pylint: disable=no-self-use,no-self-argument
    @root_validator
    def validate_either(cls, values):
        if 'policy_id' not in values and 'policy_name' not in values:
            raise ValueError('Either policy id or policy name needs to be provided')
        return values
