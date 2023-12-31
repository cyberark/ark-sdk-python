from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPALoadedPolicies(ArkModel):
    loaded_path: str = Field(description='Path to the workspace dir which the policies were loaded to')
    overall_policies_count: int = Field(description='Overall policies in the workspace')
    loaded_policies_count: int = Field(description='Loaded policies count')
    overriden_policies_count: int = Field(description='Overriden policies count')
    untouched_policies_count: int = Field(description='Policies count which were not overriden')
