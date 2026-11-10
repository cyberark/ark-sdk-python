from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import Field, PositiveInt

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common.ark_category_type import ArkCategoryType
from ark_sdk_python.models.services.ars.requests.ark_ars_request_type import ArkARSRequestType


class ArkARSWorkflowRuleState(str, Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    DRAFT = 'draft'
    EXPIRED = 'expired'


class ArkARSWorkflowRuleType(str, Enum):
    GLOBALLY_ASSOCIATED = 'globally_associated'
    POLICY_ASSOCIATED = 'policy_associated'
    PCLOUD_ASSOCIATED = 'pcloud_associated'


class ArkARSWorkflowAutomaticAction(str, Enum):
    NONE = 'none'
    APPROVE = 'approve'
    REJECT = 'reject'


class ArkARSWorkflowType(str, Enum):
    IN_APP = 'in_app'
    FLOWS = 'flows'
    PCLOUD = 'pcloud'


class ArkARSWorkflow(ArkCamelizedModel):
    workflow_type: Optional[ArkARSWorkflowType] = Field(description='The type of workflow', default=None)
    automatic_action: Optional[ArkARSWorkflowAutomaticAction] = Field(
        default=ArkARSWorkflowAutomaticAction.NONE, description='Whether this workflow should be automatically approved/rejected or not'
    )
    num_approvers: Optional[PositiveInt] = Field(description='Number of approvers required', default=None)
    workflow_id: Optional[str] = Field(default=None, description='ID of the workflow in the relevant type')
    workflow_name: Optional[str] = Field(default=None, description='Name of the workflow in the relevant type')


class ArkARSWorkflowAssociationType(str, Enum):
    POLICY = 'policy'
    ENTITY = 'entity'
    APPROVER = 'approver'


class ArkARSWorkflowAssociation(ArkCamelizedModel):
    association_id: Optional[str] = Field(default=None, description='Identifier of the association, for example policy id')


class ArkARSWorkflowApproverAssociation(ArkARSWorkflowAssociation):
    association_type: Literal[ArkARSWorkflowAssociationType.APPROVER]
    approver: Optional[Dict[str, Any]] = Field(default=None, description='Approver entity details')


class ArkARSWorkflowEntityAssociation(ArkARSWorkflowAssociation):
    association_type: Literal[ArkARSWorkflowAssociationType.ENTITY]
    entity: Optional[Dict[str, Any]] = Field(default=None, description='Entity details for entity-type associations')


class ArkARSWorkflowPolicyAssociation(ArkARSWorkflowAssociation):
    association_type: Literal[ArkARSWorkflowAssociationType.POLICY]
    policy_name: Optional[str] = Field(default=None, description='Name of the associated policy')


# A discriminator annotation is intentionally omitted because pydantic v2 does not allow Dict in a discriminated union;
# left-to-right smart-union resolution with Literal[association_type] achieves the same routing.
ArkARSWorkflowAssociationTypes = Union[
    ArkARSWorkflowApproverAssociation,
    ArkARSWorkflowEntityAssociation,
    ArkARSWorkflowPolicyAssociation,
    Dict[str, Any],
]


class ArkARSWorkflowRule(ArkCamelizedModel):
    rule_id: str = Field(description='ID of the rule')
    category_type: ArkCategoryType = Field(description='Category of the rule')
    request_type: Optional[ArkARSRequestType] = Field(description='Type of the request', default=None)
    rule_name: str = Field(description='Name of the rule')
    rule_description: str = Field(description='Description about the rule', default='')
    rule_type: ArkARSWorkflowRuleType = Field(description='Type of the rule')
    start_date: Optional[date] = Field(default=None, description='Start date in which the rule is effective')
    end_date: Optional[date] = Field(default=None, description='End date in which the rule is no longer effective')
    workflow: Optional[ArkARSWorkflow] = Field(description='Info about the workflow associated with this rule', default=None)
    rule_state: ArkARSWorkflowRuleState = Field(description='State of the workflow rule', default=ArkARSWorkflowRuleState.DRAFT)
    associations: Dict[ArkARSWorkflowAssociationType, List[Dict[str, Any]]] = Field(
        description='Entity associations to the rule', default_factory=dict
    )
    created_by: str = Field(description='Who created the rule')
    creation_time: datetime = Field(description='Creation time of the rule')
    last_updated_by: str = Field(description='Who last updated the rule')
    last_update_time: datetime = Field(description='When was the rule last updated')
