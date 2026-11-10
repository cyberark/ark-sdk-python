from typing import Optional

from pydantic import Field, model_serializer

from ark_sdk_python.models import ArkCamelizedModel


class ArkSIAK8SCluster(ArkCamelizedModel):
    cluster_address: str = Field(description='Address of the K8s cluster')
    cluster_username: str = Field(description='Username used to connect to the K8s cluster')
    is_reason_required: bool = Field(default=False, description='Whether a reason is required in order to access this cluster')
    reason: Optional[str] = Field(
        default=None,
        description='Reason for accessing the cluster, required when generating cluster access and isReasonRequired is true',
    )

    @model_serializer(mode='wrap')
    def serialize_model(self, handler) -> dict:
        data = handler(self)
        if isinstance(data, dict) and self.reason is None:
            data.pop('reason', None)
        return data
