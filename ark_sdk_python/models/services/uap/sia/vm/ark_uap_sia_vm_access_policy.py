from typing import Any, Dict

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.uap.sia.common.ark_uap_sia_common_access_policy import ArkUAPSIACommonAccessPolicy
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_behavior import (
    ArkUAPSSIAVMBehavior,
    ArkUAPSSIAVMRDPProfile,
    ArkUAPSSIAVMSSHProfile,
)
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_targets import (
    ArkUAPSIAVMAWSResource,
    ArkUAPSIAVMAzureResource,
    ArkUAPSIAVMFQDNIPResource,
    ArkUAPSIAVMGCPResource,
    ArkUAPSIAVMPlatformTargets,
)


class ArkUAPSIAVMAccessPolicy(ArkUAPSIACommonAccessPolicy):
    targets: Annotated[ArkUAPSIAVMPlatformTargets, Field(description='The targets of the vm access policy')]
    behavior: Annotated[ArkUAPSSIAVMBehavior, Field(description='Defines the behavior of a connection to the VM')]

    def serialize_model(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Serializes the model to a dictionary, including the behavior of the VM access policy.
        """
        data = super().model_dump(*args, **kwargs)
        if self.metadata.policy_entitlement.location_type == ArkWorkspaceType.AWS and self.targets.aws_resource:
            data['targets'] = {
                'AWS': self.targets.aws_resource.model_dump(*args, **kwargs),
            }
        elif self.metadata.policy_entitlement.location_type == ArkWorkspaceType.AZURE and self.targets.azure_resource:
            data['targets'] = {
                'Azure': self.targets.azure_resource.model_dump(*args, **kwargs),
            }
        elif self.metadata.policy_entitlement.location_type == ArkWorkspaceType.GCP and self.targets.gcp_resource:
            data['targets'] = {
                'GCP': self.targets.gcp_resource.model_dump(*args, **kwargs),
            }
        elif self.metadata.policy_entitlement.location_type == ArkWorkspaceType.FQDN_IP and self.targets.fqdnip_resource:
            data['targets'] = {
                'FQDN/IP': self.targets.fqdnip_resource.model_dump(*args, **kwargs),
            }
        else:
            raise ValueError('Unsupported workspace type')
        data['behavior'] = {'connectAs': {}}
        if self.behavior.ssh_profile:
            data['behavior']['connectAs']['ssh'] = self.behavior.ssh_profile.model_dump(*args, **kwargs)
        if self.behavior.rdp_profile:
            data['behavior']['connectAs']['rdp'] = self.behavior.rdp_profile.model_dump(*args, **kwargs)
        return data

    @staticmethod
    def deserialize_model(data: Dict[str, Any], *args, **kwargs) -> 'ArkUAPSIAVMAccessPolicy':
        policy = ArkUAPSIAVMAccessPolicy.model_validate(data, *args, **kwargs)
        if 'targets' in data:
            policy.targets = ArkUAPSIAVMPlatformTargets()
            if policy.metadata.policy_entitlement.location_type == ArkWorkspaceType.AWS and 'AWS' in data['targets']:
                policy.targets.aws_resource = ArkUAPSIAVMAWSResource.model_validate(data['targets']['AWS'])
            elif policy.metadata.policy_entitlement.location_type == ArkWorkspaceType.AZURE and 'Azure' in data['targets']:
                policy.targets.azure_resource = ArkUAPSIAVMAzureResource.model_validate(data['targets']['Azure'])
            elif policy.metadata.policy_entitlement.location_type == ArkWorkspaceType.GCP and 'GCP' in data['targets']:
                policy.targets.gcp_resource = ArkUAPSIAVMGCPResource.model_validate(data['targets']['GCP'])
            elif policy.metadata.policy_entitlement.location_type == ArkWorkspaceType.FQDN_IP and 'FQDN/IP' in data['targets']:
                policy.targets.fqdnip_resource = ArkUAPSIAVMFQDNIPResource.model_validate(data['targets']['FQDN/IP'])
            else:
                raise ValueError('Workspace type not found')
        if 'behavior' in data:
            policy.behavior = ArkUAPSSIAVMBehavior()
            if 'connectAs' in data['behavior']:
                if 'ssh' in data['behavior']['connectAs']:
                    policy.behavior.ssh_profile = ArkUAPSSIAVMSSHProfile.model_validate(data['behavior']['connectAs']['ssh'])
                if 'rdp' in data['behavior']['connectAs']:
                    policy.behavior.rdp_profile = ArkUAPSSIAVMRDPProfile.model_validate(data['behavior']['connectAs']['rdp'])
        return policy
