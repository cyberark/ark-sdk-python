import re
from typing import Final, Optional

from pydantic import Field, model_validator

from ark_sdk_python.models import ArkModel

VAULTED_ACCOUNT_ID_REGEX: Final[str] = r'^[0-9]+_[0-9]+$'


class ArkSIASSOGetShortLivedRDPFile(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=True)
    folder: str = Field(description='Output folder to write the rdp file to')
    target_address: str = Field(description='Address of the Windows target machine')
    target_domain: Optional[str] = Field(default=None, description='Domain of the Windows target machine')
    target_user: Optional[str] = Field(default=None, description='Name of the target user to connect with')
    vaulted_account_id: Optional[str] = Field(default=None, description='ID of the vaulted account to connect with, requires a target user')
    elevated_privileges: Optional[bool] = Field(default=None, description='whether to run session with elevated privileges')

    # pylint: disable=no-self-use,no-self-argument
    @model_validator(mode='after')
    def validate_vaulted_account_id(self):
        if self.vaulted_account_id is not None:
            if not self.target_user:
                raise ValueError('Vaulted account id requires a target user to be given as well')
            if not re.fullmatch(VAULTED_ACCOUNT_ID_REGEX, self.vaulted_account_id):
                raise ValueError('Vaulted account id must be of the format <safe id>_<account id>, for example 10_10')
        return self
