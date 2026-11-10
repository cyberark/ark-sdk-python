from typing import List, Optional

from pydantic import Field, model_serializer, model_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_principal import ArkUAPPrincipal


class ArkUAPAccessApproval(ArkCamelizedModel):
    required: bool = Field(default=False, description='Whether access approval is required before granting access')
    approvers: Optional[List[ArkUAPPrincipal]] = Field(default=None, description='Optional list of principals who can approve access')

    @model_validator(mode='after')
    def validate_approvers(self):
        if self.required and self.approvers is not None and len(self.approvers) == 0:
            raise ValueError('approvers cannot be empty when required is true')
        return self

    @model_serializer(mode='wrap')
    def serialize_model(self, handler) -> dict:
        data = handler(self)
        if isinstance(data, dict) and data.get('approvers') is None:
            data.pop('approvers', None)
        return data
