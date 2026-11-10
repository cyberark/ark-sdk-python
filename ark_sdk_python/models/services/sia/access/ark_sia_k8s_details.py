from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr


class ArkSIAK8sDetails(ArkModel):
    """
    Kubernetes-specific configuration for a k8s-ephemeral connector.
    All fields are optional; when supplied they skip the corresponding interactive prompt in the setup script.
    """

    upgrade: Optional[bool] = Field(
        default=False, description='When true, passes --upgrade to the K8s setup script to upgrade an existing installation'
    )
    k8s_namespace: Optional[str] = Field(
        default=None, description='Kubernetes namespace to install into. When supplied, skips the interactive namespace prompt'
    )
    k8s_image_uri: Optional[str] = Field(
        default=None,
        description='Full URI of the connector image (registry/repo:tag). When supplied, skips the interactive image-URI prompt',
    )
    k8s_username: Optional[str] = Field(
        default=None, description='Service user username for the K8s connector. When supplied, skips the interactive username prompt'
    )
    k8s_password: Optional[ArkSecretStr] = Field(
        default=None, description='Service user password for the K8s connector. When supplied, skips the interactive password prompt'
    )
    k8s_replicas: Optional[int] = Field(
        default=None, description='Number of connector replicas (1-10). When supplied, skips the interactive replicas prompt'
    )
    k8s_image_pull_secret: Optional[str] = Field(
        default=None,
        description='Name of an existing Kubernetes pull-secret in the connector namespace. When supplied, skips the interactive prompt',
    )
