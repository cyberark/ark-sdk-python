from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkWorkspaceType

ArkSIAVMKeyValTag = Dict[str, Union[str, List[str], Optional[str], Optional[List[str]]]]


class ArkSIAVMAWSProviderData(ArkCamelizedModel):
    provider_name: Literal['AWS'] = Field(alias='providerName', default='AWS', exclude=True)
    regions: Optional[List[str]] = Field(default=None, description='Regions AWS Filter')
    tags: Optional[List[ArkSIAVMKeyValTag]] = Field(default=None, description='Tags AWS Filter')
    vpc_ids: Optional[List[str]] = Field(default=None, description='VPCs AWS Filter')
    account_ids: Optional[List[str]] = Field(default=None, description='Accounts AWS Filter')


class ArkSIAVMAzureProviderData(ArkCamelizedModel):
    provider_name: Literal['Azure'] = Field(alias='providerName', default='Azure', exclude=True)
    azure_regions: Optional[List[str]] = Field(default=None, description='Regions Azure Filter')
    azure_tags: Optional[List[ArkSIAVMKeyValTag]] = Field(default=None, description='Tags Azure Filter')
    azure_resource_groups: Optional[List[str]] = Field(default=None, description='Resources Groups Azure Filter')
    azure_vnet_ids: Optional[List[str]] = Field(default=None, description='Vnets Azure Filter')
    azure_subscriptions: Optional[List[str]] = Field(default=None, description='Subscriptions Azure Filter')


class ArkSIAVMGCPProviderData(ArkCamelizedModel):
    provider_name: Literal['GCP'] = Field(alias='providerName', default='GCP', exclude=True)
    regions: Optional[List[str]] = Field(default=None, description='Regions GCP Filter')
    labels: Optional[List[Dict]] = Field(default=None, description='Labels GCP Filter')
    vpc_ids: Optional[List[str]] = Field(default=None, description='Vpc GCP Filter')
    projects: Optional[List[str]] = Field(default=None, description='Projects GCP Filter')


class ArkSIAVMFQDNOperator(str, Enum):
    EXACTLY = 'EXACTLY'
    WILDCARD = 'WILDCARD'
    PREFIX = 'PREFIX'
    SUFFIX = 'SUFFIX'
    CONTAINS = 'CONTAINS'


class ArkSIAVMIpOperator(str, Enum):
    EXACTLY = 'EXACTLY'
    WILDCARD = 'WILDCARD'


class ArkSIAVMFQDNRule(ArkCamelizedModel):
    operator: Optional[ArkSIAVMFQDNOperator] = Field(default=None, description='Operator to perform on the FQDN')
    computername_pattern: Optional[str] = Field(default=None, description='The pattern in relations to the operator')
    domain: Optional[str] = Field(default=None, description='The domain in which to execute the operator on the pattern')


class ArkSIAVMIpRule(ArkCamelizedModel):
    operator: ArkSIAVMIpOperator = Field(description='Operator to perform on the ip+logical name')
    ip_addresses: List[str] = Field(description='IP address to match the logical name')
    logical_name: str = Field(description='Network logical name to match the ip address')


class ArkSIAVMOnPremProviderData(ArkCamelizedModel):
    provider_name: Literal['OnPrem'] = Field(alias='providerName', default='OnPrem', exclude=True)
    fqdn_rules: Optional[List[ArkSIAVMFQDNRule]] = Field(default=None, description='List of FQDN rules applied to the policy')
    logical_names: Optional[List[str]] = Field(default=None, description='List of logical network names applied to the policy')
    ip_rules: Optional[List[ArkSIAVMIpRule]] = Field(default=None, description='List of ip rules applied to the policy')


ArkSIAVMProvider = Annotated[
    Union[ArkSIAVMAWSProviderData, ArkSIAVMAzureProviderData, ArkSIAVMGCPProviderData, ArkSIAVMOnPremProviderData],
    Field(discriminator='provider_name'),
]
ArkSIAVMProvidersDict = Dict[ArkWorkspaceType, ArkSIAVMProvider]
