import base64
import json
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union

from humps.main import camelize
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    PlainSerializer,
    SecretBytes,
    SecretStr,
    TypeAdapter,
    field_validator,
)
from typing_extensions import Annotated

from ark_sdk_python.models import ArkException


class ArkModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class ArkGenericModel(ArkModel, BaseModel):
    pass


class ArkPresentableModel(ArkModel):
    model_config = ConfigDict(use_enum_values=True)


class ArkCamelizedModel(ArkPresentableModel):
    model_config = ConfigDict(alias_generator=camelize)


class ArkTitleizedModel(ArkPresentableModel):
    model_config = ConfigDict(alias_generator=lambda s: s.replace("_", " ").title().replace(" ", ""))


def secret_serializer(s: Optional[Union[str, SecretStr, SecretBytes]]) -> Union[str, bytes]:
    if not s:
        return None
    if isinstance(s, (str, bytes)):
        return s
    return s.get_secret_value()


def base64_serializer(data: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a base64-encoded JSON string.

    Args:
        data (Dict[str, Any]): The dictionary to serialize.

    Returns:
        str: The base64-encoded JSON string.

    Raises:
        ArkException: If there is an error during serialization.
    """
    try:
        json_bytes = json.dumps(data).encode('utf-8')
        base64_bytes = base64.b64encode(json_bytes)
        return base64_bytes.decode('utf-8')
    except (TypeError, ValueError) as e:
        raise ArkException(f'Error encoding data to base64: {e}') from e


ArkPollCallback = Callable
ArkSecretStr = Annotated[SecretStr, PlainSerializer(func=secret_serializer, return_type=str)]
ArkSecretBytes = Annotated[SecretBytes, PlainSerializer(func=secret_serializer, return_type=bytes)]
ArkB64SerializedDict = Annotated[Dict[str, Any], PlainSerializer(base64_serializer, return_type=str)]
ArkHttpUrlString = Annotated[str, BeforeValidator(lambda value: str(TypeAdapter(HttpUrl).validate_python(value)))]
ArkSerializableDatetime = Annotated[datetime, PlainSerializer(lambda v: v.strftime('%FT%T%z'))]


class ArkPollableModel(ArkCamelizedModel):
    poll: Optional[bool] = Field(default=None, description='Whether to poll for any async api action')
    poll_timeout_seconds: Optional[int] = Field(description='For how long to poll in seconds', default=3600)
    poll_progress_callback: Optional[Any] = Field(
        default=None,
        description='Callback for poll progression, '
        'sends the current async task, '
        'seconds remaining whether the poll operation '
        'finished or not and whether the operation was successful '
        'or not, Note that its set to any due to pydantic internal prints',
    )
    poll_allow_refreshable_connection: Optional[bool] = Field(
        default=None,
        description='Whether to allow authentication refreshing during poll operations '
        'This is useful for when the poll operation is long and prolongs the actual token time',
    )

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('poll_progress_callback', mode="before")
    @classmethod
    def poll_callback_must_be_callable(cls, v):
        if v is not None and not isinstance(v, ArkPollCallback):
            raise ValueError('Must be callable')
        return v
