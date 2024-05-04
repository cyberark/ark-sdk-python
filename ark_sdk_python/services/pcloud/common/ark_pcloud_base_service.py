import os
from typing import Literal

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.common.env import AwsEnv
from ark_sdk_python.common.isp.ark_isp_service_client import ArkISPServiceClient
from ark_sdk_python.services.ark_service import ArkService


class ArkPCloudBaseService(ArkService):
    def __init__(
        self,
        isp_auth: ArkISPAuth,
        base_api_path: Literal['api', 'webservices'] = 'api',
    ) -> None:
        super().__init__(isp_auth)
        env = None
        if 'env' in isp_auth.token.metadata.keys():
            env = isp_auth.token.metadata['env']
        else:
            env = os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value)
        self._client = ArkISPServiceClient(
            service_name='privilegecloud',
            token=isp_auth.token.token.get_secret_value(),
            tenant_env=AwsEnv(env),
            base_path=f'passwordvault/{base_api_path}/',
        )
