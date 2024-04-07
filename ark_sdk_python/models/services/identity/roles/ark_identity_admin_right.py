from enum import Enum


class ArkIdentityAdminRights(str, Enum):
    AdminPortalLogin = '/lib/rights/adminportallogin.json'
    RoleManagement = '/lib/rights/roleman.json'
    ReadOnlyRoleManagement = '/lib/rights/roroleman.json'
    UserManagement = '/lib/rights/dsman.json'
    Audit = 'ServiceRight/auditShowTile'
    JIT = 'ServiceRight/dpaShowTile'
