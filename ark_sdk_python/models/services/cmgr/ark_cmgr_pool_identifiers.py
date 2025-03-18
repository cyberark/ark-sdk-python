from enum import Enum
from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkCmgrPoolIdentifierType(str, Enum):
    GENERAL_FQDN = 'GENERAL_FQDN'
    GENERAL_HOSTNAME = 'GENERAL_HOSTNAME'
    AWS_ACCOUNT_ID = 'AWS_ACCOUNT_ID'
    AWS_VPC = 'AWS_VPC'
    AWS_SUBNET = 'AWS_SUBNET'
    AZURE_SUBSCRIPTION = 'AZURE_SUBSCRIPTION'
    AZURE_VNET = 'AZURE_VNET'
    AZURE_SUBNET = 'AZURE_SUBNET'
    GCP_PROJECT = 'GCP_PROJECT'
    GCP_NETWORK = 'GCP_NETWORK'
    GCP_SUBNET = 'GCP_SUBNET'


class ArkCmgrPoolIdentifier(ArkCamelizedModel):
    id: str = Field(description='ID of the identifier')
    pool_id: str = Field(description='ID of the pool this identifier is associated to')
    type: ArkCmgrPoolIdentifierType = Field(description='Type of the identifier')
    value: str = Field(description='Value of the identifier')
    created_at: str = Field(description='The creation time of the identifier')
    updated_at: str = Field(description='The last update time of the identifier')


class ArkCmgrPoolIdentifiers(ArkCamelizedModel):
    identifiers: List[ArkCmgrPoolIdentifier] = Field(description='Identifiers List')
