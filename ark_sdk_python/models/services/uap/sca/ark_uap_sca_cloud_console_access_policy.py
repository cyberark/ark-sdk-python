from typing import Any, Dict, List, Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models.services.uap.common.ark_uap_common_access_policy import ArkUAPCommonAccessPolicy
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_cloud_invalid_resources import ArkUAPSCACloudInvalidResources
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_conditions import ArkUAPSCAConditions
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_targets import (
    ArkUAPSCAAWSAccountTarget,
    ArkUAPSCAAWSOrganizationTarget,
    ArkUAPSCAAzureTarget,
    ArkUAPSCAAzureWorkspaceTypesValues,
    ArkUAPSCACloudConsoleTarget,
    ArkUAPSCAGCPTarget,
    ArkUAPSCAGCPWorkspaceTypesValues,
)
from ark_sdk_python.models.services.uap.utils import serialize_uap_policies_workspace_type


class ArkUAPSCACloudConsoleAccessPolicy(ArkUAPCommonAccessPolicy):
    conditions: ArkUAPSCAConditions = Field(
        default_factory=ArkUAPSCAConditions, description='The time and session conditions of the policy'
    )
    targets: Annotated[ArkUAPSCACloudConsoleTarget, Field(description='The targeted cloud provider and workspace')]
    invalid_resources: Optional[ArkUAPSCACloudInvalidResources] = Field(
        default=None, description='Resources that are not valid for the policy'
    )

    def serialize_model(self, *args, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(*args, **kwargs)

        # Fixing location type serialization
        data['metadata']['policyEntitlement']['locationType'] = serialize_uap_policies_workspace_type(
            self.metadata.policy_entitlement.location_type
        )

        all_targets: List[Dict[str, Any]] = []
        targets_to_append = (
            self.targets.gcp_targets + self.targets.azure_targets + self.targets.aws_organization_targets + self.targets.aws_account_targets
        )

        for target in targets_to_append:
            target_data = target.model_dump(*args, **kwargs)
            all_targets.append(target_data)

        del data['targets']['gcpTargets']
        del data['targets']['azureTargets']
        del data['targets']['awsOrganizationTargets']
        del data['targets']['awsAccountTargets']

        data['targets']['targets'] = all_targets

        return data

    @staticmethod
    def deserialize_model(data: Dict[str, Any], *args, **kwargs) -> 'ArkUAPSCACloudConsoleAccessPolicy':
        policy = ArkUAPSCACloudConsoleAccessPolicy.model_validate(data, *args, **kwargs)

        if 'targets' in data and 'targets' in data['targets']:
            for target in data['targets']['targets']:
                # Azure and GCP targets are identified by 'workspace_type' field existence.
                if 'workspaceType' in target:
                    if target['workspaceType'] in ArkUAPSCAAzureWorkspaceTypesValues:
                        current_target = ArkUAPSCAAzureTarget.model_validate(target)
                        policy.targets.azure_targets.append(current_target)
                    elif target['workspaceType'] in ArkUAPSCAGCPWorkspaceTypesValues:
                        current_target = ArkUAPSCAGCPTarget.model_validate(target)
                        policy.targets.gcp_targets.append(current_target)
                    else:
                        raise ValueError(f"Unknown workspace type in cloud console targets: [{target['workspaceType']}]")
                # AWS Organization targets are identified by 'org_id' field existence and without 'workspace_type' field existence.
                elif 'orgId' in target:
                    current_target = ArkUAPSCAAWSOrganizationTarget.model_validate(target)
                    policy.targets.aws_organization_targets.append(current_target)
                # AWS Account targets are identified by 'workspace_id' existence and no 'org_id' nor 'workspace_type' fields existence.
                elif 'workspaceId' in target:
                    current_target = ArkUAPSCAAWSAccountTarget.model_validate(target)
                    policy.targets.aws_account_targets.append(current_target)
                else:
                    raise ValueError('Unknown target type in cloud console targets')

        return policy
