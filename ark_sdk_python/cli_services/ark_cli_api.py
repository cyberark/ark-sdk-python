from __future__ import annotations

from ark_sdk_python.ark_api import ArkAPI


class ArkCLIAPI(ArkAPI):
    @property
    def dpa_policies_db_editor(self) -> "ArkDPADBPoliciesEditorService":
        """
        DB policy editor CLI service

        Returns:
            ArkDPADBPoliciesEditorService: _description_
        """
        from ark_sdk_python.cli_services.dpa.db import ArkDPADBPoliciesEditorService

        return ArkDPADBPoliciesEditorService(self.authenticator('isp'), profile=self.profile)
