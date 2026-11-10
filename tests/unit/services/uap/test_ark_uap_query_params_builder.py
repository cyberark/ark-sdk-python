import unittest

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_request import (
    ArkUAPFilters,
    ArkUAPGetAccessPoliciesRequest,
    ArkUAPGetQueryParams,
)
from ark_sdk_python.models.services.uap.common.ark_uap_policy_type import ArkUAPPolicyType
from ark_sdk_python.models.services.uap.common.ark_uap_status_type import ArkUAPStatusType


class TestQueryParamsBuilder(unittest.TestCase):

    def test_build_filter_query_with_multiple_values(self):
        filters = ArkUAPFilters(location_type=[ArkWorkspaceType.AWS, ArkWorkspaceType.AZURE], status=[ArkUAPStatusType.ACTIVE])
        result = filters.build_filter_query_from_filters()
        expected = "(((locationType eq 'AWS') or (locationType eq 'Azure')) and (status eq 'Active'))"
        self.assertEqual(result, expected)

    def test_filter_query_with_contains_operator(self):
        filters = ArkUAPFilters(identities=["user1", "user2"])
        result = filters.build_filter_query_from_filters()
        expected = "((identities contains 'user1') or (identities contains 'user2'))"
        self.assertEqual(result, expected)

    def test_filter_query_single_value_no_or(self):
        filters = ArkUAPFilters(status=[ArkUAPStatusType.ACTIVE])
        result = filters.build_filter_query_from_filters()
        expected = "(status eq 'Active')"
        self.assertEqual(result, expected)

    def test_filter_query_ignores_none_and_empty_lists(self):
        filters = ArkUAPFilters(location_type=[], policy_tags=None, text_search=None)
        result = filters.build_filter_query_from_filters()
        self.assertEqual(result, "")

    def test_build_get_query_params_full_request_with_all_supported_fields(self):
        filters = ArkUAPFilters(
            location_type=[ArkWorkspaceType.AZURE],
            policy_type=[ArkUAPPolicyType.RECURRING],
            identities=["id1"],
            text_search="search",
            show_editable_policies=True,
        )
        request = ArkUAPGetAccessPoliciesRequest(filters=filters, limit=100, next_token="nt_123")
        params = request.build_get_query_params()

        self.assertIsInstance(params, ArkUAPGetQueryParams)
        self.assertEqual(params.limit, 100)
        self.assertEqual(params.q, "search")
        self.assertEqual(params.next_token, "nt_123")
        self.assertTrue(params.show_editable_policies)

        expected_filter = "((locationType eq 'Azure') and (policyType eq 'Recurring') and (identities contains 'id1'))"
        self.assertEqual(params.filter, expected_filter)

    def test_build_get_query_params_without_filters_returns_minimal(self):
        request = ArkUAPGetAccessPoliciesRequest(limit=15)
        params = request.build_get_query_params()

        self.assertEqual(params.limit, 15)
        self.assertIsNone(params.filter)
        self.assertIsNone(params.q)
        self.assertIsNone(params.show_editable_policies)

    def test_build_query_respects_show_editable_policies_false(self):
        filters = ArkUAPFilters(show_editable_policies=False)
        request = ArkUAPGetAccessPoliciesRequest(filters=filters)
        params = request.build_get_query_params()

        self.assertFalse(params.show_editable_policies)
