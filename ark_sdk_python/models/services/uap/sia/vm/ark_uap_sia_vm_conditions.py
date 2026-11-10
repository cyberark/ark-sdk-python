from typing import Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models.services.uap.sia.common.ark_uap_sia_common_conditions import ArkUAPSIACommonConditions


class ArkUAPSIAVMConditions(ArkUAPSIACommonConditions):
    """
    VM-specific policy conditions. Extends the shared SIA infrastructure conditions
    with session recording override controls that are only applicable to VM policies.
    """

    override_recording: Annotated[
        Optional[bool],
        Field(
            default=None,
            description='When true, the policy recording value overrides the tenant-level session recording setting.',
        ),
    ] = None
    recording: Annotated[
        Optional[bool],
        Field(
            default=None,
            description='Enables or disables session recording for connections matched by this policy. Only applied when override_recording is true. None means use the tenant default.',
        ),
    ] = None
