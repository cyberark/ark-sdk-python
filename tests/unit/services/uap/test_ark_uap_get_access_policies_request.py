import unittest

from ark_sdk_python.models.common import ArkCategoryType, ArkWorkspaceType
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_request import ArkUAPFilters, ArkUAPGetAccessPoliciesRequest
from ark_sdk_python.models.services.uap.common.ark_uap_policy_type import ArkUAPPolicyType
from ark_sdk_python.models.services.uap.common.ark_uap_status_type import ArkUAPStatusType


class TestGetAccessPoliciesRequest(unittest.TestCase):

    def test_filters_with_all_fields(self):
        filters_data = {
            "locationType": ["AWS"],
            "targetCategory": ["Cloud console"],
            "policyType": ["Recurring"],
            "policyTags": ["tag1", "tag2"],
            "identities": ["user1", "user2"],
            "status": ["Active"],
            "textSearch": "search_text",
            "showEditablePolicies": False,
        }

        filters = ArkUAPFilters(**filters_data)

        self.assertEqual(filters.location_type, [ArkWorkspaceType.AWS])
        self.assertEqual(filters.target_category, [ArkCategoryType.CLOUD_CONSOLE])
        self.assertEqual(filters.policy_type, [ArkUAPPolicyType.RECURRING])
        self.assertEqual(filters.policy_tags, ["tag1", "tag2"])
        self.assertEqual(filters.identities, ["user1", "user2"])
        self.assertEqual(filters.status, [ArkUAPStatusType.ACTIVE])
        self.assertEqual(filters.text_search, "search_text")
        self.assertFalse(filters.show_editable_policies)

    def test_get_access_policies_request_with_aliases(self):
        request_data = {"filters": {"locationType": ["AWS"], "textSearch": "test"}, "limit": 25, "nextToken": "abc123"}

        request = ArkUAPGetAccessPoliciesRequest(**request_data)
        filters: ArkUAPFilters = getattr(request, 'filters', None)

        self.assertEqual(request.limit, 25)
        self.assertEqual(request.next_token, "abc123")
        self.assertEqual(filters.location_type, [ArkWorkspaceType.AWS])
        self.assertEqual(filters.text_search, "test")

    def test_get_access_policies_request_defaults(self):
        request = ArkUAPGetAccessPoliciesRequest()

        self.assertEqual(request.limit, 50)
        self.assertIsNone(request.filters)
        self.assertIsNone(request.next_token)

    def test_filters_model_dump_by_alias(self):
        filters = ArkUAPFilters(location_type=[ArkWorkspaceType.AWS], show_editable_policies=True, text_search="admin")
        dumped = filters.model_dump(by_alias=True)
        self.assertEqual(dumped["locationType"], ["AWS"])
        self.assertEqual(dumped["showEditablePolicies"], True)
        self.assertEqual(dumped["textSearch"], "admin")
