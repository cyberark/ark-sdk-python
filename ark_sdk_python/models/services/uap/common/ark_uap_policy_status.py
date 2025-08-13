from typing import Optional

from pydantic import Field, constr

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_status_type import ArkUAPStatusType


class ArkUAPPolicyStatus(ArkCamelizedModel):
    status: ArkUAPStatusType = Field(description='The status type of the policy')
    status_code: Optional[constr(max_length=100)] = Field(default=None, description='The status code of the policy')
    status_description: Optional[constr(max_length=1000)] = Field(default=None, description='The status description of the policy')
    link: Optional[constr(max_length=255)] = Field(default=None, description='A documentation link for the policy status')
