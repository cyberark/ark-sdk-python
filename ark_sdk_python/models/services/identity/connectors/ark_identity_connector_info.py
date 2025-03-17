from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkIdentityConnectorInfo(ArkTitleizedModel):
    ad_proxy: Optional[str] = Field(default=None, description='Whether ad proxy is enabled', alias='ADProxy')
    app_gateway: Optional[str] = Field(default=None, description='Whether app gateway is enabled')
    bandwidth_kbps: Optional[float] = Field(default=None, description='KB/s bandwidth of the connector')
    branding: Optional[str] = Field(default=None, description='Branding of the connector')
    customer_name: Optional[str] = Field(default=None, description='Name of the customer of the connector')
    dns_host_name: str = Field(description='DNS of the connector')
    forest: str = Field(description='Forest of the connector')
    connector_id: str = Field(description='ID of the connector', alias='ID')
    iwa_enabled: Optional[bool] = Field(default=None, description='Whether iwa is enabled')
    iwa_hostname: Optional[str] = Field(default=None, description='Iwa hostname')
    iwa_http_port: Optional[int] = Field(default=None, description='Iwa http port')
    iwa_port: Optional[int] = Field(default=None, description='Iwa port')
    ldap_proxy: Optional[str] = Field(default=None, description='Whether ldap proxy is enabled', alias='LDAPProxy')
    machine_name: str = Field(description='Machine name of the connector')
    name: str = Field(description='Name of the connector')
    online: bool = Field(description='Whether the connector is online or not')
    version: str = Field(description='Version of the connector')
    rdp_service: Optional[str] = Field(default=None, description='Whether RDP service is enabled', alias='RDPService')
    on_prem_api_proxy_service: Optional[str] = Field(default=None, description='Whether on prem api proxy is enabled')
    win_net_proxy_service: Optional[str] = Field(default=None, description='Whether win network proxy service is enabled')
