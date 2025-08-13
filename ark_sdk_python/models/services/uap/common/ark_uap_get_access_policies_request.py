from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkCategoryType, ArkWorkspaceType
from ark_sdk_python.models.services.uap.common.ark_uap_policy_type import ArkUAPPolicyType
from ark_sdk_python.models.services.uap.common.ark_uap_status_type import ArkUAPStatusType
from ark_sdk_python.models.services.uap.utils.ark_uap_policies_workspace_type_serializer import serialize_uap_policies_workspace_types


class ArkUAPFilterOperator(str, Enum):
    EQ = "eq"
    CONTAINS = "contains"
    OR = "or"
    AND = "and"


class ArkUAPGetQueryParams(ArkCamelizedModel):
    filter: Annotated[Optional[str], Field(default=None, description="The filter query to apply on the policies")]
    show_editable_policies: Annotated[Optional[bool], Field(default=None, description="Show editable policies")]
    q: Annotated[Optional[str], Field(default=None, description="Free text search on policy name or description ")]
    next_token: Annotated[Optional[str], Field(default=None, description="The next token for pagination")]
    limit: Annotated[int, Field(description="The maximum number of policies to return in the response")]


class ArkUAPFilters(ArkCamelizedModel):
    location_type: Annotated[
        Optional[List[ArkWorkspaceType]], Field(default=None, description='List of wanted location types for the policies')
    ]
    target_category: Annotated[
        Optional[List[ArkCategoryType]], Field(default=None, description='List of wanted target categories for the policies')
    ]
    policy_type: Annotated[
        Optional[List[ArkUAPPolicyType]], Field(default=None, description='List of wanted policy types for the policies')
    ]
    policy_tags: Annotated[Optional[List[str]], Field(default=None, description='List of wanted policy tags for the policies')]
    identities: Annotated[Optional[List[str]], Field(default=None, description='List of identities to filter the policies by')]
    status: Annotated[Optional[List[ArkUAPStatusType]], Field(default=None, description='List of wanted policy statuses for the policies')]
    text_search: Annotated[
        Optional[str], Field(default=None, description='Text search filter to apply on the policies names and descriptions')
    ]
    show_editable_policies: Annotated[Optional[bool], Field(default=None, description='Whether to show editable policies or not')]
    max_pages: Annotated[int, Field(default=1000000, description='The maximum number of pages for pagination, default is 1000000')]

    def model_dump(self, **kwargs) -> dict:
        data = super().model_dump(**kwargs)
        data['locationType'] = serialize_uap_policies_workspace_types(self.location_type)
        return data

    __FILTER_OPERATORS: Dict[str, ArkUAPFilterOperator] = {
        "locationType": ArkUAPFilterOperator.EQ,
        "policyType": ArkUAPFilterOperator.EQ,
        "targetCategory": ArkUAPFilterOperator.EQ,
        "policyTags": ArkUAPFilterOperator.EQ,
        "status": ArkUAPFilterOperator.EQ,
        "identities": ArkUAPFilterOperator.CONTAINS,
    }

    __MAP_ALIAS_TO_FIELD_NAME: Dict[str, str] = {
        "locationType": "location_type",
        "policyType": "policy_type",
        "targetCategory": "target_category",
        "policyTags": "policy_tags",
        "status": "status",
        "identities": "identities",
    }

    def build_filter_query_from_filters(self) -> str:
        """
        Summary : Builds a filter query string from the provided filters.

        Returns: the filter query string constructed from the filters.

        """
        clauses = []

        for field_name, operator in self.__FILTER_OPERATORS.items():
            values = getattr(self, self.__MAP_ALIAS_TO_FIELD_NAME.get(field_name), None)
            if field_name == "locationType":
                values = serialize_uap_policies_workspace_types(values) if values else None
            if values:
                item_clauses = [f"({field_name} {operator.value} '{v}')" for v in values]
                joined = f" {ArkUAPFilterOperator.OR.value} ".join(item_clauses)
                clauses.append(f"({joined})" if len(item_clauses) > 1 else item_clauses[0])

        return f"({' and '.join(clauses)})" if len(clauses) > 1 else (clauses[0] if clauses else "")


class ArkUAPGetAccessPoliciesRequest(ArkCamelizedModel):
    filters: Optional[ArkUAPFilters] = Field(default=None, description="The filter query to apply on the policies")
    limit: int = Field(default=50, description="The maximum number of policies to return in the response")
    next_token: Optional[str] = Field(default=None, description="The next token for pagination")

    def build_get_query_params(self) -> ArkUAPGetQueryParams:
        """
        Summary: Builds the query parameters for retrieving access policies.

        This method constructs the query parameters based on the provided filters and pagination options.


        Returns:
            ArkUAPGetQueryParams: The constructed query parameters for the access policies request.
        """

        query_params = ArkUAPGetQueryParams(limit=self.limit)
        if not self.filters:
            return query_params

        local_filters: ArkUAPFilters = getattr(self, 'filters', None)

        if local_filters.text_search:
            query_params.q = local_filters.text_search

        filter_query = local_filters.build_filter_query_from_filters()
        if filter_query:
            query_params.filter = filter_query

        if self.next_token:
            query_params.next_token = self.next_token

        if local_filters.show_editable_policies is not None:
            query_params.show_editable_policies = local_filters.show_editable_policies

        return query_params
