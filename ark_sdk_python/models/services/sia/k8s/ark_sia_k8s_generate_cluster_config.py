from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAK8SGenerateClusterConfig(ArkModel):
    clusters_file: str = Field(
        description='Path to a JSON file describing the clusters to access, in the same format returned by the list clusters '
        'command, with an additional "reason" field filled in per cluster where a reason is required'
    )
    folder: Optional[str] = Field(default=None, description='Output folder to download the generated kube config file to')
