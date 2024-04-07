"""Module to define the data models from the API."""

from __future__ import annotations

__all__ = [
    "Response",
]

import abc
import dataclasses
import typing

from dataclasses_json import DataClassJsonMixin, LetterCase, config, dataclass_json


@typing.dataclass_transform(kw_only_default=True)
class Model(DataClassJsonMixin, abc.ABC):
    """Base class for any data model.

    This class makes sure that every subclass is registered as a dataclass as
    well as implements methods to convert/parse them from Json data."""

    def __init_subclass__(cls):
        dataclasses.dataclass(frozen=True, kw_only=True)(cls)
        dataclass_json(cls)
        return cls


class Response(Model):
    id: int
    foo_bar: str = dataclasses.field(
        metadata=config(letter_case=LetterCase.CAMEL)
    )
