import html
from typing import Optional

from pydantic import Field, conlist, constr, field_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_change_info import ArkUAPChangeInfo
from ark_sdk_python.models.services.uap.common.ark_uap_policy_entitlement import ArkUAPPolicyEntitlement
from ark_sdk_python.models.services.uap.common.ark_uap_policy_status import ArkUAPPolicyStatus
from ark_sdk_python.models.services.uap.common.ark_uap_time_frame import ArkUAPTimeFrame


class ArkUAPMetadata(ArkCamelizedModel):
    policy_id: Optional[constr(max_length=99)] = Field(default=None, description='Policy id')
    name: constr(min_length=1, max_length=200) = Field(description='Name of the policy')
    description: Optional[constr(max_length=200)] = Field(default=None, description='Description of the policy')
    status: ArkUAPPolicyStatus = Field(description='Status of the policy')
    time_frame: Optional[ArkUAPTimeFrame] = Field(default=None, description='The time that the policy is active')
    policy_entitlement: ArkUAPPolicyEntitlement = Field(description='The policy target category, location type and policy type')
    created_by: Optional[ArkUAPChangeInfo] = Field(default=None, description='The user who created the policy, and the creation time')
    updated_on: Optional[ArkUAPChangeInfo] = Field(default=None, description='The user who updated the policy, and the update time')
    policy_tags: Optional[conlist(str, max_length=20)] = Field(default_factory=list, description='List of tags that related to the policy')
    time_zone: constr(max_length=50, pattern=r'\w+') = Field(default='GMT', description='The time zone of the policy, default is GMT')

    @field_validator('policy_tags', mode='before')
    @classmethod
    def _filter_none_policy_tags(cls, v):
        if v is None:
            return v
        return [tag for tag in v if tag is not None]

    @field_validator('name')
    @classmethod
    def _encode_name(cls, v):
        return html.escape(v) if v else v

    @field_validator('description')
    @classmethod
    def _encode_description(cls, v):
        return html.escape(v) if v else v
