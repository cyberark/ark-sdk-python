from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIATestConnectorReachability(ArkModel):
    connector_id: str = Field(description='The id of the connector to test')
    target_hostname: Optional[str] = Field(default=None, description='Target hostname to test the connector against')
    target_port: Optional[int] = Field(default=22, description='Target port to test the connector against')
    check_backend_endpoints: Optional[bool] = Field(default=False, description='Whether to check the backend endpoints as well')


class ArkSIAEndpoint(ArkModel):
    status: Optional[str] = Field(default=None, description='Status of the backend connector endpoint test')
    description: Optional[str] = Field(default=None, description='Description of the backend connector endpoint test')
    latency_mlsec: Optional[int] = Field(default=-1, description='Latency in milliseconds for the backend connector endpoint test')


class ArkSIABackendEndpoint(ArkSIAEndpoint):
    backend_connector_endpoint: str = Field(description='Backend connector endpoint to test the connector against')


class ArkSIATargetEndpoint(ArkSIAEndpoint):
    target_ip: str = Field(description='Target IP address to test the connector against')
    target_port: Optional[int] = Field(default=22, description='Target port to test the connector against')


class ArkSIATestConnectorReachabilityResponse(ArkModel):
    backends: Optional[List[ArkSIABackendEndpoint]] = Field(default=[], description='List of backend endpoints')
    targets: Optional[List[ArkSIATargetEndpoint]] = Field(default=[], description='List of targets')
