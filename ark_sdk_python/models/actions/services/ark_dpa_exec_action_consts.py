from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.cli_services.dpa.policies_editor.common import (
    ArkDPACommitPolicies,
    ArkDPAEditPolicies,
    ArkDPAGetPoliciesStatus,
    ArkDPALoadPolicies,
    ArkDPAPoliciesDiff,
    ArkDPARemovePolicies,
    ArkDPAResetPolicies,
    ArkDPAViewPolicies,
)
from ark_sdk_python.models.cli_services.dpa.policies_editor.db import ArkDPADBGeneratePolicy
from ark_sdk_python.models.cli_services.dpa.policies_editor.vm import ArkDPAVMGeneratePolicy
from ark_sdk_python.models.services.dpa.certificates import (
    ArkDPACertificatesFilter,
    ArkDPACreateCertificate,
    ArkDPADeleteCertificate,
    ArkDPAGetCertificate,
    ArkDPAUpdateCertificate,
)
from ark_sdk_python.models.services.dpa.db import (
    ArkDPADBMysqlExecution,
    ArkDPADBOracleGenerateAssets,
    ArkDPADBProxyFullchainGenerateAssets,
    ArkDPADBPsqlExecution,
)
from ark_sdk_python.models.services.dpa.k8s.ark_dpa_k8s_generate_kubeconfig import ArkDPAK8SGenerateKubeConfig
from ark_sdk_python.models.services.dpa.policies.common import ArkDPADeletePolicy, ArkDPAGetPolicy, ArkDPAUpdatePolicyStatus
from ark_sdk_python.models.services.dpa.policies.db import ArkDPADBAddPolicy, ArkDPADBPoliciesFilter, ArkDPADBUpdatePolicy
from ark_sdk_python.models.services.dpa.policies.vm import ArkDPAVMAddPolicy, ArkDPAVMPoliciesFilter, ArkDPAVMUpdatePolicy
from ark_sdk_python.models.services.dpa.secrets.db import (
    ArkDPADBAddSecret,
    ArkDPADBDeleteSecret,
    ArkDPADBDisableSecret,
    ArkDPADBEnableSecret,
    ArkDPADBGetSecret,
    ArkDPADBSecretsFilter,
    ArkDPADBUpdateSecret,
)
from ark_sdk_python.models.services.dpa.sso import (
    ArkDPASSOGetShortLivedClientCertificate,
    ArkDPASSOGetShortLivedOracleWallet,
    ArkDPASSOGetShortLivedPassword,
    ArkDPASSOGetShortLivedRDPFile,
)
from ark_sdk_python.models.services.dpa.workspaces.db import (
    ArkDPADBAddDatabase,
    ArkDPADBDatabasesFilter,
    ArkDPADBDeleteDatabase,
    ArkDPADBGetDatabase,
    ArkDPADBUpdateDatabase,
)

WORKSPACES_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-database': ArkDPADBAddDatabase,
    'delete-database': ArkDPADBDeleteDatabase,
    'update-database': ArkDPADBUpdateDatabase,
    'list-databases': None,
    'list-databases-by': ArkDPADBDatabasesFilter,
    'database': ArkDPADBGetDatabase,
    'databases-stats': None,
}
WORKSPACES_DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='db', schemas=WORKSPACES_DB_ACTION_TO_SCHEMA_MAP
)
WORKSPACES_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='workspaces', subactions=[WORKSPACES_DB_ACTION]
)
POLICIES_VM_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-policy': ArkDPAVMAddPolicy,
    'delete-policy': ArkDPADeletePolicy,
    'update-policy': ArkDPAVMUpdatePolicy,
    'update-policy-status': ArkDPAUpdatePolicyStatus,
    'policy': ArkDPAGetPolicy,
    'list-policies': None,
    'list-policies-by': ArkDPAVMPoliciesFilter,
    'policies-stats': None,
}
POLICIES_VM_EDITOR_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'load-policies': ArkDPALoadPolicies,
    'generate-policy': ArkDPAVMGeneratePolicy,
    'edit-policies': ArkDPAEditPolicies,
    'remove-policies': ArkDPARemovePolicies,
    'view-policies': ArkDPAViewPolicies,
    'reset-policies': ArkDPAResetPolicies,
    'policies-diff': ArkDPAPoliciesDiff,
    'policies-status': ArkDPAGetPoliciesStatus,
    'commit-policies': ArkDPACommitPolicies,
}
POLICIES_VM_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='vm',
    schemas=POLICIES_VM_ACTION_TO_SCHEMA_MAP,
    subactions=[ArkServiceActionDefinition(action_name='editor', schemas=POLICIES_VM_EDITOR_ACTION_TO_SCHEMA_MAP)],
)
POLICIES_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-policy': ArkDPADBAddPolicy,
    'delete-policy': ArkDPADeletePolicy,
    'update-policy': ArkDPADBUpdatePolicy,
    'update-policy-status': ArkDPAUpdatePolicyStatus,
    'policy': ArkDPAGetPolicy,
    'list-policies': None,
    'list-policies-by': ArkDPADBPoliciesFilter,
    'policies-stats': None,
}
POLICIES_DB_EDITOR_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'load-policies': ArkDPALoadPolicies,
    'generate-policy': ArkDPADBGeneratePolicy,
    'edit-policies': ArkDPAEditPolicies,
    'remove-policies': ArkDPARemovePolicies,
    'view-policies': ArkDPAViewPolicies,
    'reset-policies': ArkDPAResetPolicies,
    'policies-diff': ArkDPAPoliciesDiff,
    'policies-status': ArkDPAGetPoliciesStatus,
    'commit-policies': ArkDPACommitPolicies,
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
    'add-certificate': ArkDPACreateCertificate,
    'delete-certificate': ArkDPADeleteCertificate,
    'update-certificate': ArkDPAUpdateCertificate,
    'list-certificates': None,
    'list-certificates-by': ArkDPACertificatesFilter,
    'certificate': ArkDPAGetCertificate,
}
CERTIFICATES_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='certificates', schemas=CERTIFICATES_ACTION_TO_SCHEMA_MAP
)
SECRETS_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'add-secret': ArkDPADBAddSecret,
    'update-secret': ArkDPADBUpdateSecret,
    'delete-secret': ArkDPADBDeleteSecret,
    'enable-secret': ArkDPADBEnableSecret,
    'disable-secret': ArkDPADBDisableSecret,
    'secret': ArkDPADBGetSecret,
    'list-secrets': None,
    'list-secrets-by': ArkDPADBSecretsFilter,
    'secrets-stats': None,
}
SECRETS_DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='db', schemas=SECRETS_DB_ACTION_TO_SCHEMA_MAP)
SECRETS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='secrets', subactions=[SECRETS_DB_ACTION])
SSO_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'short-lived-password': ArkDPASSOGetShortLivedPassword,
    'short-lived-client-certificate': ArkDPASSOGetShortLivedClientCertificate,
    'short-lived-oracle-wallet': ArkDPASSOGetShortLivedOracleWallet,
    'short-lived-rdp-file': ArkDPASSOGetShortLivedRDPFile,
}
SSO_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='sso', schemas=SSO_ACTION_TO_SCHEMA_MAP)
DB_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {
    'psql': ArkDPADBPsqlExecution,
    'mysql': ArkDPADBMysqlExecution,
    'generate-oracle-tnsnames': ArkDPADBOracleGenerateAssets,
    'generate-proxy-fullchain': ArkDPADBProxyFullchainGenerateAssets,
}
DB_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='db', schemas=DB_ACTION_TO_SCHEMA_MAP)
K8S_ACTION_TO_SCHEMA_MAP: Final[Dict[(str, Optional[Type[ArkModel]])]] = {'generate-kubeconfig': ArkDPAK8SGenerateKubeConfig}
K8S_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(action_name='k8s', schemas=K8S_ACTION_TO_SCHEMA_MAP)
DPA_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='dpa',
    subactions=[POLICIES_ACTION, WORKSPACES_ACTION, SECRETS_ACTION, SSO_ACTION, DB_ACTION, CERTIFICATES_ACTION, K8S_ACTION],
)
