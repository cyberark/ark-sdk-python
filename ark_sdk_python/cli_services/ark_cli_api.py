from __future__ import annotations

from ark_sdk_python.ark_api import ArkAPI


class ArkCLIAPI(ArkAPI):
    @property
    def sia_policies_vm_editor(self) -> "ArkSIAVMPoliciesEditorService":
        """
        VM policy editor CLI service

        Returns:
            ArkSIAVMPoliciesEditorService: _description_
        """
        from ark_sdk_python.cli_services.sia.vm import ArkSIAVMPoliciesEditorService

        return ArkSIAVMPoliciesEditorService(self.authenticator('isp'), profile=self.profile)

    @property
    def sia_policies_db_editor(self) -> "ArkSIADBPoliciesEditorService":
        """
        DB policy editor CLI service

        Returns:
            ArkSIADBPoliciesEditorService: _description_
        """
        from ark_sdk_python.cli_services.sia.db import ArkSIADBPoliciesEditorService

        return ArkSIADBPoliciesEditorService(self.authenticator('isp'), profile=self.profile)
