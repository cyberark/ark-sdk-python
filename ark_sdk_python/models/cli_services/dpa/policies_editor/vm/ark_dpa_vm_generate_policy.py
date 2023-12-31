from typing import Optional, Set

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.cli_services.dpa.policies_editor.common.ark_dpa_base_generate_policy import ArkDPABaseGeneratePolicy


class ArkDPAVMGeneratePolicy(ArkDPABaseGeneratePolicy):
    providers: Optional[Set[Literal['AWS', 'Azure', 'OnPrem']]] = Field(description='Providers to generate the policy for')
    protocols: Optional[Set[Literal['ssh', 'rdp']]] = Field(description='Protocols to generate the policy for')
