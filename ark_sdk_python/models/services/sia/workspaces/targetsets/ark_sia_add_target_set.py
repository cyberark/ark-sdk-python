from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm import ArkSIAVMSecretType
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_target_set_type import ArkSIATargetSetType


class ArkSIAAddTargetSet(ArkModel):
    name: str = Field(description='Name of the target set')
    description: Optional[str] = Field(default=None, description='Description about the target set')
    provision_format: Optional[str] = Field(default=None, description='Provisioning format of the target set')
    enable_certificate_validation: Optional[bool] = Field(
        default=None, description='Whether to enable certificate validation for the target set'
    )
    secret_type: Optional[ArkSIAVMSecretType] = Field(default=None, description='Secret type of the target set')
    secret_id: Optional[str] = Field(default=None, description='Secret id of the target set')
    type: ArkSIATargetSetType = Field(description='Type of the target set', default=ArkSIATargetSetType.DOMAIN)
