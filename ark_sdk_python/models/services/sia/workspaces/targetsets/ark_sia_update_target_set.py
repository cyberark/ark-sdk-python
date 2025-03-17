from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.secrets.vm import ArkSIAVMSecretType
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_target_set_type import ArkSIATargetSetType


class ArkSIAUpdateTargetSet(ArkModel):
    name: str = Field(description='Name of the target set to update')
    new_name: Optional[str] = Field(default=None, description='New name for the target set')
    description: Optional[str] = Field(default=None, description='Updated description of the target set')
    provision_format: Optional[str] = Field(default=None, description='New provisioning format for the target set')
    enable_certificate_validation: Optional[bool] = Field(default=None, description='Updated enabling certificate validation')
    secret_type: Optional[ArkSIAVMSecretType] = Field(ddefault=None, escription='Secret type to update')
    secret_id: Optional[str] = Field(default=None, description='Secret id to update')
    type: ArkSIATargetSetType = Field(description='Type of the target set', default=ArkSIATargetSetType.DOMAIN)
