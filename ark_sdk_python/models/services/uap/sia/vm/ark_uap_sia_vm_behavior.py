from typing import List, Optional

from pydantic import Field, model_validator
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel


class ArkUAPSSIAVMSSHProfile(ArkCamelizedModel):
    """
    Defines the SSH profile for this virtual machine access policy. This profile is used to connect to the VM via SSH.
    """

    username: str = Field(description='Username which the user will connect with on the certificate')


class ArkUAPSSIAVMEphemeralUser(ArkCamelizedModel):
    """
    Defines the ephemeral user method related data for this virtual machine access policy.
    """

    assign_groups: List[str] = Field(description='Predefined assigned local groups of the user', default_factory=list)
    enable_ephemeral_user_reconnect: bool = Field(description='Whether the ephemeral user can reconnect', default=False)


class ArkUAPSSIAVMDomainEphemeralUser(ArkUAPSSIAVMEphemeralUser):
    """
    Defines the domain ephemeral user method related data for this virtual machine access policy.
    """

    assign_domain_groups: List[str] = Field(description='Predefined assigned domain groups of the user', default_factory=list)


class ArkUAPSSIAVMRDPProfile(ArkCamelizedModel):
    """
    Defines the RDP profile for this virtual machine access policy. This profile is used to connect to the VM via RDP.
    """

    local_ephemeral_user: Optional[ArkUAPSSIAVMEphemeralUser] = Field(description='Local ephemeral user method related data', default=None)
    domain_ephemeral_user: Optional[ArkUAPSSIAVMDomainEphemeralUser] = Field(
        description='Domain ephemeral user method related data', default=None
    )

    @model_validator(mode='after')
    @classmethod
    def validate_data(cls, values):
        if not values.domain_ephemeral_user and not values.local_ephemeral_user:
            raise ValueError('At least one of domainEphemeralUser or localEphemeralUser must be provided')
        if values.domain_ephemeral_user and values.local_ephemeral_user:
            raise ValueError('Only one of domainEphemeralUser or localEphemeralUser can be provided')
        return values


class ArkUAPSSIAVMBehavior(ArkCamelizedModel):
    """
    Defines the behavior of a virtual machine access policy, including SSH and RDP profiles.
    """

    ssh_profile: Annotated[
        Optional[ArkUAPSSIAVMSSHProfile], Field(description='The SSH profile for this virtual machine access policy')
    ] = None
    rdp_profile: Annotated[
        Optional[ArkUAPSSIAVMRDPProfile], Field(description='The RDP profile for this virtual machine access policy')
    ] = None
