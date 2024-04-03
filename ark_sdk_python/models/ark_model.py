from typing import Any, Callable, Optional

from humps import camelize
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel


class ArkModel(BaseModel):
    class Config:
        allow_population_by_field_name = True


class ArkGenericModel(ArkModel, GenericModel):
    pass


class ArkPresentableModel(ArkModel):
    class Config:
        use_enum_values = True


class ArkCamelizedModel(ArkPresentableModel):
    class Config:
        alias_generator = camelize


class ArkTitleizedModel(ArkPresentableModel):
    class Config:
        alias_generator = lambda s: s.replace("_", " ").title().replace(" ", "")


ArkPollCallback = Callable


class ArkPollableModel(ArkCamelizedModel):
    poll: Optional[bool] = Field(description='Whether to poll for any async api action')
    poll_timeout_seconds: Optional[int] = Field(description='For how long to poll in seconds', default=3600)
    poll_progress_callback: Optional[Any] = Field(
        description='Callback for poll progression, '
        'sends the current async task, '
        'seconds remaining whether the poll operation '
        'finished or not and whether the operation was successful '
        'or not, Note that its set to any due to pydantic internal prints'
    )
    poll_allow_refreshable_connection: Optional[bool] = Field(
        description='Whether to allow authentication refreshing during poll operations '
        'This is useful for when the poll operation is long and prolongs the actual token time'
    )

    # pylint: disable=no-self-use,no-self-argument
    @validator('poll_progress_callback')
    def poll_callback_must_be_callable(cls, v):
        if v is not None and not isinstance(v, ArkPollCallback):
            raise ValueError('Must be callable')
        return v
