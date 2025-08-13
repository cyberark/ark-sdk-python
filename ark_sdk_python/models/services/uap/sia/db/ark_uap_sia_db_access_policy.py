from typing import Any, Dict

from pydantic import Field, field_validator
from typing_extensions import Annotated

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.uap.sia.common.ark_uap_sia_common_access_policy import ArkUAPSIACommonAccessPolicy
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_targets import ArkUAPSIADBTargets


class ArkUAPSIADBAccessPolicy(ArkUAPSIACommonAccessPolicy):
    targets: Annotated[Dict[ArkWorkspaceType, ArkUAPSIADBTargets], Field(description='The targets of the db access policy')]

    @field_validator('targets', mode='before')
    @classmethod
    def validate_workspace_type(cls, val: Dict[str, Any]):
        if val is not None:
            for key in val.keys():
                if ArkWorkspaceType(key) not in [ArkWorkspaceType.FQDN_IP]:
                    raise ValueError('Invalid Workspace Type')
        return val

    def serialize_model(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Serializes the model to a dictionary, including the profiles of each instance in the targets.
        Done to customize serialization of each instance's profile.
        This ensures that each instance's profile is serialized according to its authentication method,
        and included in the output under the 'profile' key.
        """
        data = super().model_dump(*args, **kwargs)

        for workspace_type, target in self.targets.items():
            serialized_instances = []
            for index, instance in enumerate(target.instances):
                profile = instance.profile_by_authentication_method()
                if profile is None:
                    raise ValueError(
                        f'No profile found for the given authentication method, instance: [{instance.instance_name}], authentication method: [{instance.authentication_method}]'
                    )

                instance_data = instance.model_dump(
                    *args,
                    **kwargs,
                )
                data['targets'][workspace_type]['instances'][index]['profile'] = profile.model_dump(*args, **kwargs)
                del data['targets'][workspace_type]['instances'][index][
                    instance.auth_method_to_profile_field_name()[instance.authentication_method]
                ]
                serialized_instances.append(instance_data)

        return data
