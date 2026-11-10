from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory


class ArkARSQueryValueType(str, Enum):
    string = 'STRING'
    text = 'TEXT'
    choice = 'CHOICE'
    datetime = 'DATETIME'
    date = 'DATE'
    time = 'TIME'
    timezone = 'TIMEZONE'
    integer = 'INTEGER'
    bool = 'BOOL'
    list = 'LIST'
    any = 'ANY'


class ArkARSQueryBinaryOperator(str, Enum):
    and_ = 'AND'
    or_ = 'OR'


class ArkARSRegexCondition(ArkCamelizedModel):
    name: str = Field(default='regex_condition', description='Name of the condition')
    key: str = Field(description='Key name (id) of the question')
    condition: str = Field(description='Regex pattern to match the value of the answer')


class ArkARSConditionalField(ArkCamelizedModel):
    operator: ArkARSQueryBinaryOperator = Field(default=ArkARSQueryBinaryOperator.and_, description='Operator to use for the conditions')
    conditions: List[ArkARSRegexCondition] = Field(description='List of conditions to check')


class ArkARSValueValidator(ArkCamelizedModel):
    name: str = Field(description='Name of the validator')


class ArkARSSurveyQuestion(ArkCamelizedModel):
    key: str = Field(description='Key name / id of the question')
    required: Union[bool, ArkARSConditionalField] = Field(description='Whether this is a required question or not')
    default: Optional[Any] = Field(default=None, description='Default value for the question')
    title: Optional[str] = Field(default=None, description='Title of the question')
    description: Optional[str] = Field(default=None, description='Description of the question')
    value_type: Optional[ArkARSQueryValueType] = Field(default=None, description='Type of the response value')
    value_choices: Optional[List[Any]] = Field(default=None, description='If the value is a choice, what are the possible choices')
    validators: Optional[List[ArkARSValueValidator]] = Field(default=None, description='Validators for the question')


class ArkARSSurvey(ArkCamelizedModel):
    questions: List[ArkARSSurveyQuestion] = Field(description='Questions required answering on the survey')


class ArkARSAccessRequestSurvey(ArkCamelizedModel):
    request_form: ArkARSSurvey = Field(description='The category request form')
    target_category: ArkTargetCategory = Field(description='Type of category the survey is related to')
