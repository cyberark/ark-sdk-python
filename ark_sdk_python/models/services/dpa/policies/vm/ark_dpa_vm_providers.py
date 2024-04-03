from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkWorkspaceType

ArkDPAVMKeyValTag = Dict[str, Union[str, List[str], Optional[str], Optional[List[str]]]]


class ArkDPAVMAWSProviderData(ArkCamelizedModel):
    provider_name: Literal['AWS'] = Field(alias='providerName', default='AWS', exclude=True)
    regions: Optional[List[str]] = Field(description='Regions AWS Filter')
    tags: Optional[List[ArkDPAVMKeyValTag]] = Field(description='Tags AWS Filter')
    vpc_ids: Optional[List[str]] = Field(description='VPCs AWS Filter')
    account_ids: Optional[List[str]] = Field(description='Accounts AWS Filter')


class ArkDPAVMAzureProviderData(ArkCamelizedModel):
    provider_name: Literal['Azure'] = Field(alias='providerName', default='Azure', exclude=True)
    regions: Optional[List[str]] = Field(description='Regions Azure Filter')
    tags: Optional[List[ArkDPAVMKeyValTag]] = Field(description='Tags Azure Filter')
    resource_groups: Optional[List[str]] = Field(description='Resources Groups Azure Filter')
    vnet_ids: Optional[List[str]] = Field(description='Vnets Azure Filter')
    subscriptions: Optional[List[str]] = Field(description='Subscriptions Azure Filter')


class ArkDPAVMGCPProviderData(ArkCamelizedModel):
    provider_name: Literal['GCP'] = Field(alias='providerName', default='GCP', exclude=True)
    regions: Optional[List[str]] = Field(description='Regions GCP Filter')
    labels: Optional[List[Dict]] = Field(description='Labels GCP Filter')
    vpc_Ids: Optional[List[str]] = Field(description='Vpc GCP Filter')
    projects: Optional[List[str]] = Field(description='Projects GCP Filter')


class ArkDPAVMFQDNOperator(str, Enum):
    EXACTLY = 'EXACTLY'
    WILDCARD = 'WILDCARD'
    PREFIX = 'PREFIX'
    SUFFIX = 'SUFFIX'
    CONTAINS = 'CONTAINS'


class ArkDPAVMFQDNRule(ArkCamelizedModel):
    operator: Optional[ArkDPAVMFQDNOperator] = Field(description='Operator to perform on the FQDN')
    computername_pattern: Optional[str] = Field(description='The pattern in relations to the operator')
    domain: Optional[str] = Field(description='The domain in which to execute the operator on the pattern')


class ArkDPAVMOnPremProviderData(ArkCamelizedModel):
    provider_name: Literal['OnPrem'] = Field(alias='providerName', default='OnPrem', exclude=True)
    fqdn_rules: Optional[List[ArkDPAVMFQDNRule]] = Field(description='List of FQDN rules applied to the connection')


ArkDPAVMProvider = Annotated[
    Union[ArkDPAVMAWSProviderData, ArkDPAVMAzureProviderData, ArkDPAVMGCPProviderData, ArkDPAVMOnPremProviderData],
    Field(discriminator='provider_name'),
]
ArkDPAVMProvidersDict = Dict[ArkWorkspaceType, ArkDPAVMProvider]
