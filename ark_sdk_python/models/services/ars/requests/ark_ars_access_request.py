from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from humps.main import decamelize
from pydantic import Field, field_validator, model_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory
from ark_sdk_python.models.services.ars.rules.ark_ars_workflow_rule import ArkARSWorkflowAssociationType


class ArkARSAccessRequestState(str, Enum):
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    PENDING = 'PENDING'
    FULFILLING = 'FULFILLING'
    REVERTING_FULFILLMENT = 'REVERTING_FULFILLMENT'
    FINISHED = 'FINISHED'
    EXPIRED = 'EXPIRED'


class ArkARSAccessRequestResult(str, Enum):
    FULFILLED = 'FULFILLED'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    CANCELED = 'CANCELED'
    FAILED = 'FAILED'
    UNKNOWN = 'UNKNOWN'


class ArkARSAccessRequest(ArkCamelizedModel):
    request_id: str = Field(description='ID of the request')
    target_category: ArkTargetCategory = Field(description='Target category the request is related to')
    request_link: Optional[str] = Field(description='Link to the request itself', default=None)
    request_rule: Optional[str] = Field(description='Rule associated with this request', default=None)
    request_state: ArkARSAccessRequestState = Field(description='Current request state')
    request_result: ArkARSAccessRequestResult = Field(description='Result of the request', default=ArkARSAccessRequestResult.UNKNOWN)
    request_survey_input: Optional[Dict[str, Any]] = Field(
        description='Survey input given to this request. Deprecated: use request_details instead.', default=None, deprecated=True
    )
    request_details: Optional[Dict[str, Any]] = Field(description='Details given to this request', default=None)
    request_approvers: List[Dict[str, Any]] = Field(
        description='Related entities who approved or rejected the request', default_factory=list
    )
    request_outcomes: Optional[Dict[str, Any]] = Field(description='Outcomes of this request', default_factory=dict)
    request_steps: Dict[str, Any] = Field(description='Status in regards to the steps in the access request', default_factory=dict)
    last_executed_step: Optional[str] = Field(description='Last step that was actually executed', default=None)
    associations: Dict[ArkARSWorkflowAssociationType, List[Dict[str, Any]]] = Field(
        description='Entity associations to the request', default_factory=dict
    )
    finalization_reason: Optional[str] = Field(description='Reason for canceling or rejecting or approving the request', default=None)
    requester: Optional[Dict[str, Any]] = Field(description='The requester of the request', default=None)
    created_by: str = Field(description='Who created the request')
    created_at: datetime = Field(description='Creation time of the request')
    updated_by: str = Field(description='Who last updated the request')
    updated_at: datetime = Field(description='When was the request last updated')

    @staticmethod
    def _validate_dict_snake_case(v):
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError('Value must be a dictionary')
        snake_case_dict = {}
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError('All keys must be strings')
            snake_case_key = decamelize(key)
            snake_case_dict[snake_case_key] = value
        return snake_case_dict

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('request_survey_input', mode='before')
    def validate_request_survey_input(cls, v):
        return cls._validate_dict_snake_case(v)

    @field_validator('request_details', mode='before')
    def validate_request_details(cls, v):
        return cls._validate_dict_snake_case(v)

    @model_validator(mode='after')
    def sync_request_fields(self):
        if self.request_details is None and self.request_survey_input is not None:
            self.request_details = self.request_survey_input
        return self
