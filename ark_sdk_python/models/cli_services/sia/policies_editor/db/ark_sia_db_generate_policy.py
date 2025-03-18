from typing import Optional, Set

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.cli_services.sia.policies_editor.common.ark_sia_base_generate_policy import ArkSIABaseGeneratePolicy


class ArkSIADBGeneratePolicy(ArkSIABaseGeneratePolicy):
    providers: Optional[Set[Literal['MySQL', 'MariaDB', 'Postgres', 'MSSQL', 'Oracle', 'DB2', 'Mongo']]] = Field(
        default=None, description='Providers to generate the policy for'
    )
