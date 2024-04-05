"""Represent the utilities services for an authorized utility customer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, Undefined, config, dataclass_json

from utility_api.models.object_types.general_types import (
    ServiceType,
    Status,
)
from utility_api.models.object_types.meter_types import (
    FrequencyType,
    PrepayType,
    SupplierType,
)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class OngoingMonitoring:
    """Ongoing monitoring settings for a meter."""

    fixed_refresh_day: Optional[str]
    frequency: FrequencyType
    prepay: Optional[PrepayType] = None
    next_prepay: Optional[datetime] = field(
        metadata=config(field_name="next_prepay", decoder=datetime.fromisoformat),
        default=None,
    )
    next_refresh: Optional[datetime] = field(
        metadata=config(field_name="next_refresh", decoder=datetime.fromisoformat),
        default=None,
    )


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Base:
    """Basic information about the meter."""

    billing_account: str
    billing_address: Optional[str]
    billing_contact: Optional[str]
    meter_numbers: List[str]
    service_address: str
    service_class: ServiceType
    service_identifier: str
    service_tariff: str


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class ElectricDetail:
    """Information about the electric service provided to this meter."""

    voltage: float


@dataclass
class SupplierInfo(DataClassJsonMixin):
    """Information about any third party or CCA suppliers this meter has."""

    supplier_name: str
    supplier_type: SupplierType
    supplier_service_id: Optional[str] = None
    supplier_tariff: Optional[str] = None


@dataclass
class Meter(DataClassJsonMixin):
    """Represent a utility meter or similar service."""

    authorization_uid: str
    bill_count: int
    bill_coverage: List[time]
    bill_sources: List[str]
    blocks: List[str]
    created: datetime = field(
        metadata=config(field_name="created", decoder=datetime.fromisoformat)
    )
    exports: Dict[str, str]  # will be deprecated
    exports_list: List[Dict[str, Any]]  # will be deprecated
    interval_count: int
    interval_coverage: List[time]
    interval_sources: List[str]
    is_activated: bool
    is_archived: bool
    is_expanded: bool
    notes: List[Dict[str, str]]
    ongoing_monitoring: OngoingMonitoring
    status: Status
    status_message: str
    status_ts: datetime = field(
        metadata=config(field_name="status_ts", decoder=datetime.fromisoformat)
    )
    uid: str
    user_email: str
    user_uid: str
    utility: str
    base: Optional[Base] = None
    electric_details: Optional[ElectricDetail] = None
    programs: Optional[List[Dict[str, str]]] = None
    suppliers: Optional[List[SupplierInfo]] = None


@dataclass
class MetersListing(DataClassJsonMixin):
    """Outermost representation for a Utilities Meters object."""

    meters: List[Meter]
    next: Optional[str]
