from typing import Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType
from ark_sdk_python.models.services.sia.access.ark_sia_k8s_details import ArkSIAK8sDetails


class ArkSIAInstallConnector(ArkModel):
    connector_type: ArkWorkspaceType = Field(description='The type of the platform for the connector to be installed in')
    connector_os: ArkOsType = Field(description='The type of the operating system for the connector to be installed on')
    connector_pool_id: Optional[str] = Field(
        default=None,
        description='The connector pool which the connector will be part of, '
        'if not given, the connector will be assigned to the default one',
    )
    k8s_details: Optional[ArkSIAK8sDetails] = Field(
        default=None,
        description='Kubernetes configuration used when connector_os is k8s-ephemeral. Forwarded to the setup-script API so the '
        'returned script is pre-configured with these values; the script is then run locally instead of over a target machine '
        'connection',
    )
    target_machine: Optional[str] = Field(
        default=None, description='Target machine on which to install the connector on. Required unless connector_os is k8s-ephemeral'
    )
    username: Optional[str] = Field(
        default=None, description='Username to connect with to the target machine. Required unless connector_os is k8s-ephemeral'
    )
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
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
