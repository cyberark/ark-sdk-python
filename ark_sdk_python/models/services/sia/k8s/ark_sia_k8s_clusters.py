from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.k8s.ark_sia_k8s_cluster import ArkSIAK8SCluster


class ArkSIAK8SClusters(ArkModel):
    clusters: List[ArkSIAK8SCluster] = Field(default_factory=list, description='List of K8s clusters')
