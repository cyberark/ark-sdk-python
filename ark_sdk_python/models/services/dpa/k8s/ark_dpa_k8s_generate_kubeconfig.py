from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPAK8SGenerateKubeConfig(ArkModel):
    folder: str = Field(description='Output folder to download the kube config file', default=None)
