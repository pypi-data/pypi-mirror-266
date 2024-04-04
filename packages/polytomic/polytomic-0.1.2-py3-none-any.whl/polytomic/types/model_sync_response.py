# This file was auto-generated from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from .filter import Filter
from .identity import Identity
from .model_sync_field import ModelSyncField
from .override import Override
from .schedule import Schedule
from .target import Target

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class ModelSyncResponse(pydantic.BaseModel):
    active: typing.Optional[bool] = None
    fields: typing.Optional[typing.List[ModelSyncField]] = None
    filter_logic: typing.Optional[str] = None
    filters: typing.Optional[typing.List[Filter]] = None
    id: typing.Optional[str] = None
    identity: typing.Optional[Identity] = None
    mode: typing.Optional[str] = None
    name: typing.Optional[str] = None
    organization_id: typing.Optional[str] = None
    override_fields: typing.Optional[typing.List[ModelSyncField]] = None
    overrides: typing.Optional[typing.List[Override]] = None
    policies: typing.Optional[typing.List[str]] = None
    schedule: typing.Optional[Schedule] = None
    sync_all_records: typing.Optional[bool] = None
    target: typing.Optional[Target] = None

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        extra = pydantic.Extra.allow
        json_encoders = {dt.datetime: serialize_datetime}
