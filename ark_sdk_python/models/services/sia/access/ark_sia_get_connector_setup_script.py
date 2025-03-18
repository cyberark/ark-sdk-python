from typing import Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType


class ArkSIAGetConnectorSetupScript(ArkModel):
    connector_type: ArkWorkspaceType = Field(
        description='The type of the platform for the connector to be installed in', default=ArkWorkspaceType.AWS
    )
    connector_os: ArkOsType = Field(
        description='The type of the operating system for the connector to be installed on', default=ArkOsType.LINUX
    )
    connector_pool_id: Optional[str] = Field(
        description='The connector pool which the connector will be part of, '
        'if not given, the connector will be assigned to the default one',
        default='',
    )

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('connector_type', mode="before")
    @classmethod
    def validate_connector_type(cls, val):
        if val is not None:
            if ArkWorkspaceType(val) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
                ArkWorkspaceType.FAULT,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
            return ArkWorkspaceType(val)
        return val
