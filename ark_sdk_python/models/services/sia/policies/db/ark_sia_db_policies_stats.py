from typing import Dict

from pydantic import Field, field_validator

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policies_stats import ArkSIABasePoliciesStats


class ArkSIADBPoliciesStats(ArkSIABasePoliciesStats):
    policies_count_per_provider: Dict[ArkWorkspaceType, int] = Field(description='Policies count per DB platform')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('policies_count_per_provider', mode="before")
    @classmethod
    def validate_policies_count_per_provider(cls, val):
        if val is not None:
            new_val = []
            for plat in val:
                if ArkWorkspaceType(plat) not in [
                    ArkWorkspaceType.MYSQL,
                    ArkWorkspaceType.MARIADB,
                    ArkWorkspaceType.POSTGRES,
                    ArkWorkspaceType.MSSQL,
                    ArkWorkspaceType.ORACLE,
                    ArkWorkspaceType.MONGO,
                    ArkWorkspaceType.DB2,
                ]:
                    raise ValueError('Invalid Database Type')
                new_val.append(ArkWorkspaceType(plat))
            return new_val
        return val
