from typing import Optional, Set

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.cli_services.sia.policies_editor.common.ark_sia_base_generate_policy import ArkSIABaseGeneratePolicy


class ArkSIAVMGeneratePolicy(ArkSIABaseGeneratePolicy):
    providers: Optional[Set[Literal['AWS', 'Azure', 'GCP', 'OnPrem']]] = Field(
        default=None, description='Providers to generate the policy for'
    )
    protocols: Optional[Set[Literal['ssh', 'rdp']]] = Field(default=None, description='Protocols to generate the policy for')
