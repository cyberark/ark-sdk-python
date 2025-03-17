from enum import Enum
from typing import Literal, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


# ArkSIAConnectorModeCodes
class ArkSIASSOShortLiveClientCertificateFormat(str, Enum):
    FILE = 'file'
    SINGLE_FILE = 'single_file'
    RAW = 'raw'
    BASE64 = 'base64'


class ArkSIASSOGetShortLivedClientCertificate(ArkModel):
    allow_caching: bool = Field(description='Allow short lived token caching', default=False)
    folder: Optional[str] = Field(default=None, description='Output folder to write the key / certificate to. Required if format is File')
    output_format: ArkSIASSOShortLiveClientCertificateFormat = Field(
        description='The output format of the key / ' 'certificate. i.e. File, Raw, Base64',
        default=ArkSIASSOShortLiveClientCertificateFormat.FILE,
    )
    service: Literal['DPA-DB', 'DPA-K8S'] = Field(description='Which service to generate the short lived certificate for')
