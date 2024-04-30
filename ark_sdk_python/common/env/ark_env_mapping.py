import os
import re
from enum import Enum
from typing import Dict, Final


class AwsEnv(str, Enum):
    PROD = 'prod'
    GOV_PROD = 'gov-prod'


DEPLOY_ENV: Final[str] = 'DEPLOY_ENV'

EVEREST_IDENTITY_TENANT_NAME: Final[str] = 'isp'

ROOT_DOMAIN: Final[Dict[AwsEnv, str]] = {
    AwsEnv.PROD: 'cyberark.cloud',
}

SHELL_DOMAIN: Dict[AwsEnv, str] = {
    AwsEnv.PROD: ROOT_DOMAIN[AwsEnv.PROD],
}

IDENTITY_ENV_URLS: Final[Dict[AwsEnv, str]] = {
    AwsEnv.PROD: "idaptive.app",
}

IDENTITY_TENANT_NAME: Dict[AwsEnv, str] = {
    AwsEnv.PROD: EVEREST_IDENTITY_TENANT_NAME,
}

IDENTITY_GENERATED_SUFFIX_PATTERN: Dict[AwsEnv, str] = {
    AwsEnv.PROD: r"cyberark.cloud.\d.*",
}


def get_deploy_env() -> AwsEnv:
    # in case of external use of our libraries the varaible will be PLATFORM_ENV
    deploy_env = os.getenv(DEPLOY_ENV, None)
    if deploy_env is None:
        raise Exception(f"'{DEPLOY_ENV}' environment variable is not set")
    return AwsEnv(deploy_env)


def check_if_identity_generated_suffix(tenant_suffix, env: AwsEnv) -> bool:
    pattern = IDENTITY_GENERATED_SUFFIX_PATTERN.get(env)
    return re.match(pattern, tenant_suffix) is not None


def is_gov_cloud() -> bool:
    try:
        region_name = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
        return region_name.startswith('us-gov')
    except Exception:
        return False
