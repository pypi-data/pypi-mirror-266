"""Represent the meter usage intervals for an authorized user."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

from dataclasses_json import DataClassJsonMixin, config

from utility_api.models.object_types.bill_types import Unit
from utility_api.models.object_types.interval_types import (
    DataPointType,
)


@dataclass
class Base(DataClassJsonMixin):
    """Basic metadata about the interval."""

    meter_numbers: List[str]
    qualities: List[Any]
    service_address: str
    service_identifier: str
    service_tariff: str


@dataclass
class DataPoint(DataClassJsonMixin):
    """Specific value read from the meter at the time interval that contains it."""

    type: DataPointType
    unit: Unit
    value: float
    meter_number: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None


@dataclass
class Reading(DataClassJsonMixin):
    """Chunked interval reading."""

    datapoints: List[DataPoint]
    end: datetime = field(
        metadata=config(field_name="end", decoder=datetime.fromisoformat)
    )
    start: datetime = field(
        metadata=config(field_name="start", decoder=datetime.fromisoformat)
    )
    kwh: Optional[float] = None  # will be deprecated

    def datapoints_with_reading_metadata(self) -> Iterator[DataPoint]:
        """Flatten datapoints with the reading metadata.

        Yields:
            A datapoint with added reading metadata
        """
        for datapoint in self.datapoints:
            datapoint.start = self.start
            datapoint.end = self.end
            yield datapoint


@dataclass
class Interval(DataClassJsonMixin):
    """Represent the utility interval."""

    authorization_uid: str
    base: Base
    blocks: List[str]
    created: datetime = field(
        metadata=config(field_name="created", decoder=datetime.fromisoformat)
    )
    meter_uid: str
    notes: List[Any]
    readings: List[Reading]
    sources: List[Dict[str, str]]
    uid: str
    updated: datetime = field(
        metadata=config(field_name="updated", decoder=datetime.fromisoformat)
    )
    utility: str


@dataclass
class IntervalsListing(DataClassJsonMixin):
    """Outermost representation for Utilities Intervals object."""

    intervals: List[Interval]
    next: Optional[str]
    is_incomplete: bool
