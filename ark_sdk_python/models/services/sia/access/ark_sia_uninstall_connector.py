from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr
from ark_sdk_python.models.common.ark_os_type import ArkOsType


class ArkSIAUninstallConnector(ArkModel):
    connector_os: ArkOsType = Field(description='The type of the operating system for the connector is installed on')
    connector_id: Optional[str] = Field(
        default=None,
        description='Connector id to get information for uninstallation. Required unless connector_os is k8s-ephemeral, where a '
        'helm release may back multiple replica connectors with no single ID',
    )
    k8s_namespace: Optional[str] = Field(
        default=None,
        description='The Kubernetes namespace the connector was installed into. Required when connector_os is k8s-ephemeral; the '
        'connector is uninstalled by running `helm uninstall sia-connector --namespace <k8s_namespace>` locally',
    )
    username: Optional[str] = Field(
        default=None, description='Username to connect with to the target machine. Required unless connector_os is k8s-ephemeral'
    )
    target_machine: Optional[str] = Field(
        default=None,
        description='Target machine on which to uninstall the connector from, if not given, uses the connector_host_ip from the '
        'connector information. Not applicable when connector_os is k8s-ephemeral',
    )
    password: Optional[ArkSecretStr] = Field(default=None, description='Password to connect with to the target machine')
    private_key_path: Optional[str] = Field(
        default=None, description='Private key file path to use for connecting to the target machine via ssh'
    )
    private_key_contents: Optional[ArkSecretStr] = Field(
        default=None, description='Private key contents to use for connecting to the target machine via ssh'
    )
