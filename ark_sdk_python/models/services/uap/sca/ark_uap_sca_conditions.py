from ark_sdk_python.models.services.uap.common import ArkUAPConditions


class ArkUAPSCAConditions(ArkUAPConditions):
    """
    SCA-specific conditions class.

    Currently identical to ArkUAPConditions but defined separately for clarity
    and future extensibility without refactoring the ArkSCACloudConsoleAccessPolicy model.
    """
