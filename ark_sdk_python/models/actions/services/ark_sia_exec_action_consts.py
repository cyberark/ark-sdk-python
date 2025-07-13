from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.cli_services.sia.policies_editor.common import (
    ArkSIACommitPolicies,
    ArkSIAEditPolicies,
    ArkSIAGetPoliciesStatus,
    ArkSIALoadPolicies,
    ArkSIAPoliciesDiff,
    ArkSIARemovePolicies,
    ArkSIAResetPolicies,
    ArkSIAViewPolicies,
)
from ark_sdk_python.models.cli_services.sia.policies_editor.db import ArkSIADBGeneratePolicy
from ark_sdk_python.models.cli_services.sia.policies_editor.vm import ArkSIAVMGeneratePolicy
from ark_sdk_python.models.services.sia.access import ArkSIAGetConnectorSetupScript, ArkSIAInstallConnector, ArkSIAUninstallConnector
from ark_sdk_python.models.services.sia.certificates import (
    ArkSIACertificatesFilter,
    ArkSIACreateCertificate,
    ArkSIADeleteCertificate,
    ArkSIAGetCertificate,
    ArkSIAUpdateCertificate,
)
from ark_sdk_python.models.services.sia.db import (
    ArkSIADBMysqlExecution,
    ArkSIADBOracleGenerateAssets,
    ArkSIADBProxyFullchainGenerateAssets,
    ArkSIADBPsqlExecution,
)
from ark_sdk_python.models.services.sia.k8s.ark_sia_k8s_generate_kubeconfig import ArkSIAK8SGenerateKubeConfig
from ark_sdk_python.models.services.sia.policies.common import ArkSIADeletePolicy, ArkSIAGetPolicy, ArkSIAUpdatePolicyStatus
from ark_sdk_python.models.services.sia.policies.db import ArkSIADBAddPolicy, ArkSIADBPoliciesFilter, ArkSIADBUpdatePolicy
from ark_sdk_python.models.services.sia.policies.vm import ArkSIAVMAddPolicy, ArkSIAVMPoliciesFilter, ArkSIAVMUpdatePolicy
from ark_sdk_python.models.services.sia.secrets.db import (
    ArkSIADBAddSecret,
    ArkSIADBDeleteSecret,
    ArkSIADBDisableSecret,
    ArkSIADBEnableSecret,
    ArkSIADBGetSecret,
    ArkSIADBSecretsFilter,
    ArkSIADBUpdateSecret,
)
from ark_sdk_python.models.services.sia.secrets.vm import (
    ArkSIAVMAddSecret,
    ArkSIAVMChangeSecret,
    ArkSIAVMDeleteSecret,
    ArkSIAVMGetSecret,
    ArkSIAVMSecretsFilter,
)
from ark_sdk_python.models.services.sia.ssh_ca.ark_sia_get_ssh_public_key import ArkSIAGetSSHPublicKey
from ark_sdk_python.models.services.sia.sso import (
    ArkSIASSOGetShortLivedClientCertificate,
    ArkSIASSOGetShortLivedOracleWallet,
    ArkSIASSOGetShortLivedPassword,
    ArkSIASSOGetShortLivedRDPFile,
    ArkSIASSOGetSSHKey,
    ArkSIASSOGetTokenInfo,
)
from ark_sdk_python.models.services.sia.workspaces.db import (
    ArkSIADBAddDatabase,
    ArkSIADBDatabasesFilter,
    ArkSIADBDeleteDatabase,
    ArkSIADBGetDatabase,
    ArkSIADBUpdateDatabase,
)
from ark_sdk_python.models.services.sia.workspaces.targetsets import (
    ArkSIAAddTargetSet,
    ArkSIADeleteTargetSet,
    ArkSIAGetTargetSet,
    ArkSIATargetSetsFilter,
    ArkSIAUpdateTargetSet,
)
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_bulk_add_target_sets import ArkSIABulkAddTargetSetsItem
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_bulk_delete_target_sets import ArkSIABulkDeleteTargetSets

WORKSPACES_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-database': ArkSIADBAddDatabase,
    'delete-database': ArkSIADBDeleteDatabase,
    'update-database': ArkSIADBUpdateDatabase,
    'list-databases': None,
    'list-databases-by': ArkSIADBDatabasesFilter,
    'database': ArkSIADBGetDatabase,
    'databases-stats': None,
}
WORKSPACES_DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='db', schemas=WORKSPACES_DB_ACTION_TO_SCHEMA_MAP
)
WORKSPACES_TARGETSETS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-target-set': ArkSIAAddTargetSet,
    'bulk-add-target-sets': ArkSIABulkAddTargetSetsItem,
    'delete-target-set': ArkSIADeleteTargetSet,
    'bulk-delete-target-sets': ArkSIABulkDeleteTargetSets,
    'update-target-set': ArkSIAUpdateTargetSet,
    'list-target-sets': None,
    'list-target-sets-by': ArkSIATargetSetsFilter,
    'target-set': ArkSIAGetTargetSet,
    'target-sets-stats': None,
}
WORKSPACES_TARGETSETS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='target-sets',
    schemas=WORKSPACES_TARGETSETS_ACTION_TO_SCHEMA_MAP,
)
WORKSPACES_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='workspaces',
    subactions=[
        WORKSPACES_DB_ACTION,
        WORKSPACES_TARGETSETS_ACTION,
    ],
)
POLICIES_VM_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-policy': ArkSIAVMAddPolicy,
    'delete-policy': ArkSIADeletePolicy,
    'update-policy': ArkSIAVMUpdatePolicy,
    'update-policy-status': ArkSIAUpdatePolicyStatus,
    'policy': ArkSIAGetPolicy,
    'list-policies': None,
    'list-policies-by': ArkSIAVMPoliciesFilter,
    'policies-stats': None,
}
POLICIES_VM_EDITOR_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'load-policies': ArkSIALoadPolicies,
    'generate-policy': ArkSIAVMGeneratePolicy,
    'edit-policies': ArkSIAEditPolicies,
    'remove-policies': ArkSIARemovePolicies,
    'view-policies': ArkSIAViewPolicies,
    'reset-policies': ArkSIAResetPolicies,
    'policies-diff': ArkSIAPoliciesDiff,
    'policies-status': ArkSIAGetPoliciesStatus,
    'commit-policies': ArkSIACommitPolicies,
}
POLICIES_VM_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='vm',
    schemas=POLICIES_VM_ACTION_TO_SCHEMA_MAP,
    subactions=[ArkServiceActionDefinition(action_name='editor', schemas=POLICIES_VM_EDITOR_ACTION_TO_SCHEMA_MAP)],
)
POLICIES_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-policy': ArkSIADBAddPolicy,
    'delete-policy': ArkSIADeletePolicy,
    'update-policy': ArkSIADBUpdatePolicy,
    'update-policy-status': ArkSIAUpdatePolicyStatus,
    'policy': ArkSIAGetPolicy,
    'list-policies': None,
    'list-policies-by': ArkSIADBPoliciesFilter,
    'policies-stats': None,
}
POLICIES_DB_EDITOR_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'load-policies': ArkSIALoadPolicies,
    'generate-policy': ArkSIADBGeneratePolicy,
    'edit-policies': ArkSIAEditPolicies,
    'remove-policies': ArkSIARemovePolicies,
    'view-policies': ArkSIAViewPolicies,
    'reset-policies': ArkSIAResetPolicies,
    'policies-diff': ArkSIAPoliciesDiff,
    'policies-status': ArkSIAGetPoliciesStatus,
    'commit-policies': ArkSIACommitPolicies,
}
POLICIES_DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='db',
    schemas=POLICIES_DB_ACTION_TO_SCHEMA_MAP,
    subactions=[ArkServiceActionDefinition(action_name='editor', schemas=POLICIES_DB_EDITOR_ACTION_TO_SCHEMA_MAP)],
)
POLICIES_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='policies', subactions=[POLICIES_VM_ACTION, POLICIES_DB_ACTION]
)
CERTIFICATES_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-certificate': ArkSIACreateCertificate,
    'delete-certificate': ArkSIADeleteCertificate,
    'update-certificate': ArkSIAUpdateCertificate,
    'list-certificates': None,
    'list-certificates-by': ArkSIACertificatesFilter,
    'certificate': ArkSIAGetCertificate,
}
CERTIFICATES_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='certificates', schemas=CERTIFICATES_ACTION_TO_SCHEMA_MAP
)
SECRETS_VM_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-secret': ArkSIAVMAddSecret,
    'change-secret': ArkSIAVMChangeSecret,
    'delete-secret': ArkSIAVMDeleteSecret,
    'secret': ArkSIAVMGetSecret,
    'list-secrets': None,
    'list-secrets-by': ArkSIAVMSecretsFilter,
    'secrets-stats': None,
}
SECRETS_VM_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='vm',
    schemas=SECRETS_VM_ACTION_TO_SCHEMA_MAP,
)
SECRETS_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-secret': ArkSIADBAddSecret,
    'update-secret': ArkSIADBUpdateSecret,
    'delete-secret': ArkSIADBDeleteSecret,
    'enable-secret': ArkSIADBEnableSecret,
    'disable-secret': ArkSIADBDisableSecret,
    'secret': ArkSIADBGetSecret,
    'list-secrets': None,
    'list-secrets-by': ArkSIADBSecretsFilter,
    'secrets-stats': None,
}
SECRETS_DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='db', schemas=SECRETS_DB_ACTION_TO_SCHEMA_MAP)
SECRETS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='secrets',
    subactions=[
        SECRETS_DB_ACTION,
        SECRETS_VM_ACTION,
    ],
)
SSO_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'short-lived-password': ArkSIASSOGetShortLivedPassword,
    'short-lived-client-certificate': ArkSIASSOGetShortLivedClientCertificate,
    'short-lived-oracle-wallet': ArkSIASSOGetShortLivedOracleWallet,
    'short-lived-rdp-file': ArkSIASSOGetShortLivedRDPFile,
    'short-lived-token-info': ArkSIASSOGetTokenInfo,
    'short-lived-ssh-key': ArkSIASSOGetSSHKey,
}
SSO_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='sso', schemas=SSO_ACTION_TO_SCHEMA_MAP)
DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'psql': ArkSIADBPsqlExecution,
    'mysql': ArkSIADBMysqlExecution,
    'generate-oracle-tnsnames': ArkSIADBOracleGenerateAssets,
    'generate-proxy-fullchain': ArkSIADBProxyFullchainGenerateAssets,
}
DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='db', schemas=DB_ACTION_TO_SCHEMA_MAP)
K8S_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {'generate-kubeconfig': ArkSIAK8SGenerateKubeConfig}
K8S_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='k8s', schemas=K8S_ACTION_TO_SCHEMA_MAP)
ACCESS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'connector-setup-script': ArkSIAGetConnectorSetupScript,
    'install-connector': ArkSIAInstallConnector,
    'uninstall-connector': ArkSIAUninstallConnector,
}
ACCESS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='access',
    schemas=ACCESS_ACTION_TO_SCHEMA_MAP,
)
SSH_CA_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'generate-new-ca': None,
    'deactivate-previous-ca': None,
    'reactivate-previous-ca': None,
    'public-key': ArkSIAGetSSHPublicKey,
    'public-key-script': ArkSIAGetSSHPublicKey,
}
SSH_CA_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='ssh-ca',
    schemas=SSH_CA_ACTION_TO_SCHEMA_MAP,
)
SIA_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='sia',
    subactions=[
        POLICIES_ACTION,
        WORKSPACES_ACTION,
        SECRETS_ACTION,
        SSO_ACTION,
        DB_ACTION,
        CERTIFICATES_ACTION,
        K8S_ACTION,
        ACCESS_ACTION,
        SSH_CA_ACTION,
    ],
)
