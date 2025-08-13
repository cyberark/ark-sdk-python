from typing import Optional

from pydantic import Field, constr, model_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_principal_type import ArkUAPPrincipalType


class ArkUAPPrincipal(ArkCamelizedModel):
    id: constr(max_length=40) = Field(description='The id of the principal')
    name: constr(max_length=100, pattern=r'\w+') = Field(description='The name of the principal')
    source_directory_name: Optional[constr(max_length=50, pattern=r'\w+')] = Field(None, description='The name of the source directory')
    source_directory_id: Optional[str] = Field(None, description='The id of the source directory')
    type: ArkUAPPrincipalType = Field(description='The type of the principal user, group or role')

    @model_validator(mode='after')
    def validate_conditional_fields(self):
        if self.type != ArkUAPPrincipalType.ROLE:
            missing_fields = []
            if not self.source_directory_name:
                missing_fields.append('source_directory_name')
            if not self.source_directory_id:
                missing_fields.append('source_directory_id')

            if missing_fields:
                raise ValueError(f"The following fields are required for USER and GROUP: {', '.join(missing_fields)}")
        return self
