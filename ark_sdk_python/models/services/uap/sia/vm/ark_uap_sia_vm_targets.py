import re
from typing import List, Optional

from pydantic import Field, StringConstraints, field_validator
from typing_extensions import Annotated

from ark_sdk_python.common import is_ip_address
from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.vm import ArkSIAVMFQDNOperator
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_providers import ArkSIAVMIpOperator
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_consts import ERROR_MESSAGE_MUST_CONTAIN_VALUE, NETWORK_NAME_REGEX


class ArkUAPSIAVMKeyValTag(ArkCamelizedModel):
    """
    Defines a key/value pair used to match a given tag or label on a VM resource
    """

    key: str = Field(min_length=1)
    value: Optional[List[str]] = Field(default=None)


class ArkUAPSIAVMFQDNRule(ArkCamelizedModel):
    """
    Defines a specific FQDN rule used to match a given DNS record
    """

    operator: ArkSIAVMFQDNOperator = Field(description='Operator to perform on the FQDN')
    computername_pattern: Annotated[str, StringConstraints(strict=True, max_length=300)] = Field(
        description='The pattern in relations to the operator'
    )
    domain: Optional[Annotated[str, StringConstraints(strict=True, max_length=1000)]] = Field(
        description='The domain in which to execute the operator on the pattern', default=None
    )


class ArkUAPSIAVMIPRule(ArkCamelizedModel):
    """
    Defines a specific logical name rule used to match a given ip+logical name
    """

    operator: ArkSIAVMIpOperator = Field(description='Operator to perform on the ip+logical name')
    ip_addresses: Annotated[List[str], Field(max_length=1000)] = Field(description='IP address to match the logical name')
    logical_name: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=256)] = Field(
        description='Network logical name to match the ip address'
    )

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('logical_name')
    @classmethod
    def validate_logical_name(cls, logical_name):
        pattern = NETWORK_NAME_REGEX
        if logical_name is None or len(logical_name.strip()) == 0:
            raise ValueError(ERROR_MESSAGE_MUST_CONTAIN_VALUE)
        if not re.match(pattern, logical_name):
            raise ValueError('Invalid on prem logical name')
        return logical_name

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('ip_addresses')
    def validate_ip_addresses(cls, ip_addresses, values):
        if values.data.get('operator') == ArkSIAVMIpOperator.EXACTLY and (ip_addresses is None or len(ip_addresses) < 1):
            raise ValueError('ip_addresses rules list must have at least one item with operator EXACTLY')
        for ip in ip_addresses:
            if not is_ip_address(ip):
                raise ValueError(f'Invalid ip address {ip}')
        return ip_addresses


class ArkUAPSIAVMAWSResource(ArkCamelizedModel):
    """
    Represents the AWS resources for a virtual machine access policy.
    """

    regions: List[str] = Field(description='AWS region names. For example: "us-east-1". Leave empty for all regions.')
    tags: List[ArkUAPSIAVMKeyValTag] = Field(
        description='A list of key/value pairs that have been defined as custom tags for your  AWS instances. ' 'Leave empty for all tags.'
    )
    vpc_ids: List[str] = Field(description='A list of AWS VPC IDs. The accepted syntax is "vpc-<n>". Leave empty for all VPCs.')
    account_ids: List[str] = Field(description='AWS Account IDs. Leave empty for all AWS Accounts.')


class ArkUAPSIAVMAzureResource(ArkCamelizedModel):
    """
    Represents the Azure resources for a virtual machine access policy.
    """

    regions: List[str] = Field(description='Azure region names. For example: eastus2. Leave empty for all regions.')
    tags: List[ArkUAPSIAVMKeyValTag] = Field(
        description='A list of key/value pairs that have been defined as custom tags for your  Azure VMs. Leave ' 'empty for all tags'
    )
    resource_groups: List[str] = Field(description='A list of Azure resource group IDs. Leave empty for all resource groups')
    vnet_ids: List[str] = Field(description='A list of Azure VNet IDs. Leave empty for all VNets.')
    subscriptions: List[str] = Field(description='Azure subscription IDs. Leave empty for all subscriptions.')


class ArkUAPSIAVMGCPResource(ArkCamelizedModel):
    """
    Represents the GCP resources for a virtual machine access policy.
    """

    regions: List[str] = Field(description='GCP region names. For example: us-east1. Leave empty for all regions.')
    labels: List[ArkUAPSIAVMKeyValTag] = Field(
        description='A list of key/value pairs that have been defined as custom labels for your GCP VMs. ' 'Leave empty for all labels'
    )
    vpc_ids: List[str] = Field(
        description='A list of GCP VPC IDs. The accepted syntax is "projects/{project_id}/global/networks/{'
        'network_name}". Leave empty for all VPCs.'
    )
    projects: List[str] = Field(description='GCP project IDs. Leave empty for all projects.')


class ArkUAPSIAVMFQDNIPResource(ArkCamelizedModel):
    """
    Represents the fqdn/ip resources for a virtual machine access policy, including FQDN and IP rules.
    """

    fqdn_rules: Optional[List[ArkUAPSIAVMFQDNRule]] = Field(default=None, description='List of FQDN rules applied to the connection')
    ip_rules: Optional[List[ArkUAPSIAVMIPRule]] = Field(default=None, description='List of logical name rules applied to the connection')


class ArkUAPSIAVMPlatformTargets(ArkCamelizedModel):
    """
    Represents the targets for a virtual machine access policy, which can include AWS, Azure, GCP, or fqdn/ip resources.
    """

    aws_resource: Annotated[
        Optional[ArkUAPSIAVMAWSResource], Field(description='The AWS resource for this virtual machine access policy')
    ] = None
    azure_resource: Annotated[
        Optional[ArkUAPSIAVMAzureResource], Field(description='The Azure resource for this virtual machine access policy')
    ] = None
    gcp_resource: Annotated[
        Optional[ArkUAPSIAVMGCPResource], Field(description='The GCP resource for this virtual machine access policy')
    ] = None
    fqdnip_resource: Annotated[
        Optional[ArkUAPSIAVMFQDNIPResource], Field(description='The FQDN/IP resource for this virtual machine access policy')
    ] = None
