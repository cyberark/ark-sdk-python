from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAK8SGenerateKubeConfig(ArkModel):
    folder: str = Field(description='Output folder to download the kube config file', default=None)
