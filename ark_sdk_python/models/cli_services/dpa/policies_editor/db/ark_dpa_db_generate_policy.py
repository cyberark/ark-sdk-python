from typing import Optional, Set

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.cli_services.dpa.policies_editor.common.ark_dpa_base_generate_policy import ArkDPABaseGeneratePolicy


class ArkDPADBGeneratePolicy(ArkDPABaseGeneratePolicy):
    providers: Optional[Set[Literal['MySQL', 'MariaDB', 'Postgres', 'MSSQL', 'Oracle']]] = Field(
        description='Providers to generate the policy for'
    )
