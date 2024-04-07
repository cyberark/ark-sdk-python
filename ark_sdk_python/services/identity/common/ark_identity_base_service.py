import os

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.ark_client import ArkClient
from ark_sdk_python.common.env import ROOT_DOMAIN, AwsEnv
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.services.ark_service import ArkService


class ArkIdentityBaseService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self._isp_auth = isp_auth
        self._idp_client = ArkClient(
            isp_auth.token.endpoint,
            isp_auth.token.token.get_secret_value(),
        )
        self._idp_client.add_headers(
            {
                'Content-Type': 'application/json',
                'X-IDAP-NATIVE-CLIENT': 'true',
                'Authorization': f'Bearer {isp_auth.token.token.get_secret_value()}',
            }
        )
        self._client = None
        self._url_prefix = 'api/idadmin/'
        self._env = None
        if 'env' in isp_auth.token.metadata.keys():
            self._env = AwsEnv(isp_auth.token.metadata['env'])
        else:
            self._env = AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
        try:
            self._client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self._isp_auth)
            self._env = self._client.tenant_env
        except Exception:
            self._client = self._idp_client
            if any(f'id.{d}' in self._idp_client.base_url for d in ROOT_DOMAIN.values()):
                self._url_prefix = ''
