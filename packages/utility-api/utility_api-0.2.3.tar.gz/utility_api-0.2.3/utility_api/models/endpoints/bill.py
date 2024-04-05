"""Represent the utility bills for an authorizied utility customer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, Undefined, config, dataclass_json

from utility_api.models.object_types.bill_types import (
    BucketType,
    ChargeKind,
    PowerItemType,
    Unit,
)
from utility_api.models.object_types.general_types import ServiceType


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Base:
    """Basic information about the bill."""

    service_identifier: str
    service_tariff: str
    service_class: ServiceType
    service_address: str
    meter_numbers: List[str]
    billing_contact: str
    billing_address: str
    billing_account: str
    bill_start_date: datetime = field(
        metadata=config(field_name="bill_start_date", decoder=datetime.fromisoformat)
    )
    bill_end_date: datetime = field(
        metadata=config(field_name="bill_end_date", decoder=datetime.fromisoformat)
    )
    bill_total_unit: Unit
    bill_statement_date: Optional[datetime] = field(
        metadata=config(
            field_name="bill_statement_date", decoder=datetime.fromisoformat
        ),
        default=None,
    )
    bill_total_cost: Optional[float] = None
    bill_total_volume: Optional[float] = None
    bill_total_kwh: Optional[float] = None  # Will be deprecated


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class LineItem:
    """Individual charges for a bill."""

    name: str
    start: datetime = field(
        metadata=config(field_name="start", decoder=datetime.fromisoformat)
    )
    end: datetime = field(
        metadata=config(field_name="end", decoder=datetime.fromisoformat)
    )
    cost: Optional[float] = None
    volume: Optional[float] = None
    rate: Optional[float] = None
    unit: Optional[Unit] = field(
        metadata=config(field_name="unit", decoder=Unit.parse), default=None
    )
    kind: Optional[ChargeKind] = None


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Suppliers:
    """Container for information about the energy suppliers on a particular bill."""

    supplier_type: str
    supplier_line_items: List[LineItem]
    supplier_name: Optional[str] = None
    supplier_service_id: Optional[str] = None
    supplier_tariff: Optional[str] = None
    supplier_total_cost: Optional[float] = None
    supplier_total_volume: Optional[float] = None
    supplier_total_unit: Optional[Unit] = None


@dataclass
class Tier(DataClassJsonMixin):
    """Represent the method to charge customers for different amounts of usage."""

    name: str
    level: int
    cost: Optional[float] = None
    unit: Optional[Unit] = None
    volume: Optional[float] = None


@dataclass
class TimeOfUse(DataClassJsonMixin):
    """Common way to charge customers different rates at different times of the day."""

    name: str
    bucket: BucketType
    cost: Optional[float] = None
    volume: Optional[float] = None
    unit: Optional[Unit] = None


@dataclass
class Demand(DataClassJsonMixin):
    """Common way to charge customers for their power demand kW."""

    name: str
    cost: Optional[float] = None
    demand: Optional[float] = None


@dataclass
class Power(DataClassJsonMixin):
    """Listing of any reactive power or power factor information from a bill."""

    type: PowerItemType
    name: str
    volume: float
    unit: Optional[Unit]


@dataclass
class Bill(DataClassJsonMixin):
    """Represent a utility bill."""

    uid: int
    meter_uid: str
    authorization_uid: str
    created: datetime = field(
        metadata=config(field_name="created", decoder=datetime.fromisoformat)
    )
    updated: datetime = field(
        metadata=config(field_name="updated", decoder=datetime.fromisoformat)
    )
    notes: List[Any]
    utility: str
    blocks: List[str]
    base: Optional[Base] = None
    sources: Optional[List[Dict[str, Any]]] = None
    line_items: Optional[List[LineItem]] = None
    suppliers: Optional[List[Suppliers]] = None
    tiers: Optional[List[Tier]] = None
    tou: Optional[List[TimeOfUse]] = None
    demand: Optional[List[Demand]] = None
    power: Optional[List[Power]] = None
    programs: Optional[List[Dict[str, str]]] = None


@dataclass
class BillsListing(DataClassJsonMixin):
    """Outermost representation of the Utilities Bills object."""

    bills: List[Bill]
    next: Optional[str]
