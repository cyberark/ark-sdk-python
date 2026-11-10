from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAK8SListClusters(ArkModel):
    output_file: Optional[str] = Field(default=None, description='Save the clusters list as a JSON file to this path')
