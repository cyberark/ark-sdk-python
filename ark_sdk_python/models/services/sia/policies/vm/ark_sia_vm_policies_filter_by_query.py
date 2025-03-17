from typing import Final, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel

POLICIES_QUERY_MAX_LIMIT: Final[int] = 1000


class ArkSIAVMQueryPolicies(ArkModel):
    filter_string: Optional[str] = Field(
        default=None,
        description='This parameter is used to filter the policies based on specific criteria. The '
        'filter expressions must be complete within parentheses. The filter supports various '
        'operations such as equals, not equals, contains, starts with, ends with, is null, '
        'is not null, greater than and less than. The filter can be applied to various '
        'fields such as policyName, description, startDate, endDate, status, updatedBy, '
        'updatedOn, createdBy, createdOn, and platforms.  '
        'Example: ((updatedOn gt \'2024-01-01 10:00:00\') and (platforms eq \'AWS\')). '
        'For more information and examples see '
        'https://docs.cyberark.com/DPA/Latest/en/Content/APIs/dpa_policies.htm#List',
    )
    extended: Optional[bool] = Field(
        description='Whether to extended response. Extended response includes all ' 'the details of each policy.', default=False
    )
    limit: Optional[int] = Field(default=None, description='Limit the number of policies to return.', gt=0, le=POLICIES_QUERY_MAX_LIMIT)
    offset: Optional[int] = Field(default=None, description='This parameter sets the starting point of the retrieved items.')
    sort: Optional[str] = Field(
        default=None,
        description='Sort the policies based on the field. This parameter sets the sorting order of the retrieved '
        'items. The sorting order can be set to ascending (asc) or descending (desc).',
    )
