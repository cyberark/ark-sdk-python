from enum import Enum


class ArkStatus(str, Enum):
    InProgress = 'IN_PROGRESS'
    Active = 'ACTIVE'
    Deleting = 'DELETING'
    Creating = 'CREATING'
    CreateFailed = 'CREATE_FAILED'
    DeleteFailed = 'DELETE_FAILED'
    Canceled = 'CANCELED'
    Warning = 'WARNING'
    Success = 'SUCCESS'
    Successful = 'SUCCESSFUL'
    Succeeded = 'SUCCEEDED'
    Failed = 'FAILED'
    Pending = 'PENDING'
    NonActive = 'NON_ACTIVE'
    Outdated = 'OUTDATED'
    Running = 'RUNNING'
    FailoverNonRecoverableFailure = 'FAILOVER_NON_RECOVERABLE_FAILURE'
    UpgradeNonRecoverableFailure = 'UPGRADE_NON_RECOVERABLE_FAILURE'
    RollbackNonRecoverableFailure = 'ROLLBACK_NON_RECOVERABLE_FAILURE'
    FailoverNonRerunnableFailure = 'FAILOVER_NON_RERUNNABLE_FAILURE'
    UpgradeNonRerunnableFailure = 'UPGRADE_NON_RERUNNABLE_FAILURE'
    RollbackNonRerunnableFailure = 'ROLLBACK_NON_RERUNNABLE_FAILURE'
    FailoverManualApprovalRequired = 'FAILOVER_MANUAL_APPROVAL_REQUIRED'
    UpgradeManualApprovalRequired = 'UPGRADE_MANUAL_APPROVAL_REQUIRED'
    RollbackManualApprovalRequired = 'ROLLBACK_MANUAL_APPROVAL_REQUIRED'
    PreparationFailed = 'PREPARATION_FAILED'
    PreparationInProgress = 'PREPARATION_IN_PROGRESS'
    PreparationCompleted = 'PREPARATION_COMPLETED'
    DeletionFailed = 'DELETION_FAILED'
    DeletionInProgress = 'DELETION_IN_PROGRESS'
    DeletionCompleted = 'DELETION_COMPLETED'
    FailoverFailed = 'FAILOVER_FAILED'
    FailoverInProgress = 'FAILOVER_IN_PROGRESS'
    FailoverCompleted = 'FAILOVER_COMPLETED'
    UpgradeFailed = 'UPGRADE_FAILED'
    UpgradeInProgress = 'UPGRADE_IN_PROGRESS'
    UpgradeCompleted = 'UPGRADE_COMPLETED'
    RollbackFailed = 'ROLLBACK_FAILED'
    RollbackInProgress = 'ROLLBACK_IN_PROGRESS'
    RollbackCompleted = 'ROLLBACK_COMPLETED'
    UpdateFailed = 'UPDATE_FAILED'
    UpdateInProgress = 'UPDATE_IN_PROGRESS'
    UpdateCompleted = 'UPDATE_COMPLETED'
    Failover = 'FAILOVER'
    Upgrade = 'UPGRADE'
    Rollback = 'ROLLBACK'
    NotExists = 'NOT_EXISTS'
    Updating = 'UPDATING'
    Activating = 'ACTIVATING'
    Suspending = 'SUSPENDING'
    Suspended = 'SUSPENDED'
    Deleted = 'DELETED'
    Updated = 'UPDATED'
    ServiceError = 'SERVICE_ERROR'
    ServiceCreationError = 'SERVICE_CREATION_ERROR'
    TenantError = 'TENANT_ERROR'
    FailedActivating = 'FAILED_ACTIVATING'
    FailedSuspending = 'FAILED_SUSPENDING'
    FailedDeleting = 'FAILED_DELETING'
    FailedUpdating = 'FAILED_UPDATING'
    RetryingToCreate = 'RETRYING_TO_CREATE'