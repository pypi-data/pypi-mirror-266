from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeVar, Generic


class NumeratorException(Exception):
    pass


@dataclass
class VariationValue:
    booleanValue: bool | None
    stringValue: str | None
    longValue: int | None
    doubleValue: float | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VariationValue:
        return VariationValue(
            booleanValue=data.get('boolean_value'),
            stringValue=data.get('string_value'),
            longValue=data.get('long_value'),
            doubleValue=data.get('double_value'),
        )


@dataclass
class FlagVariationValue:
    key: str
    value: VariationValue
    valueType: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlagVariationValue:
        return FlagVariationValue(
            key=data.get('key'),
            value=VariationValue.from_dict(data.get('value')),
            valueType=data.get('value_type'),
        )


@dataclass
class FlagVariation:
    name: str
    value: VariationValue

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlagVariation:
        return FlagVariation(
            name=data.get('name'),
            value=VariationValue.from_dict(data.get('value')),
        )


@dataclass
class FeatureFlag:
    name: str
    key: str
    status: str
    description: str | None
    defaultOnVariation: FlagVariation
    defaultOffVariation: FlagVariation
    valueType: str
    createdAt: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureFlag:
        return FeatureFlag(
            name=data.get('name'),
            key=data.get('key'),
            status=data.get('status'),
            description=data.get('description'),
            defaultOnVariation=FlagVariation.from_dict(data.get('default_on_variation')),
            defaultOffVariation=FlagVariation.from_dict(data.get('default_off_variation')),
            valueType=data.get('value_type'),
            createdAt=datetime.strptime(data.get('created_at'), '%Y-%m-%dT%H:%M:%S.%fZ'),
        )


@dataclass
class PollingFeatureFlagResponse:
    flags: list[FlagVariationValue]
    etag: str | None

    @classmethod
    def from_dict(cls, data: dict, etag: str | None) -> PollingFeatureFlagResponse:
        return PollingFeatureFlagResponse(
            flags=list(
                map(
                    FlagVariationValue.from_dict,
                    data.get('flags'),
                )
            ),
            etag=etag,
        )


T = TypeVar('T')


@dataclass
class FlagEvaluationDetail(Generic[T]):
    key: str
    value: T
    reason: dict | None
