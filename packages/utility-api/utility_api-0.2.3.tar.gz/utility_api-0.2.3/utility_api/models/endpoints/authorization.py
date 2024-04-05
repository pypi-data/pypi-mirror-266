"""Represent the submitted authorization by utility customers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config

from utility_api.models.endpoints.meter import MetersListing
from utility_api.models.object_types.general_types import Status


@dataclass
class Authorization(DataClassJsonMixin):
    """Represent the utility account holder's authorization to share data."""

    created: datetime = field(
        metadata=config(field_name="created", decoder=datetime.fromisoformat)
    )
    customer_email: str
    expires: str
    exports: Dict[str, str]  # will be deprecated
    exports_list: List[Dict[str, str]]  # Intended for dashboard users
    is_archived: bool
    is_declined: bool
    is_expired: bool
    is_revoked: bool
    is_test: bool
    notes: List[Dict[str, str]]
    referrals: List[str]
    scope: Dict[str, str]
    status: Status
    status_message: str
    status_ts: datetime = field(
        metadata=config(field_name="status_ts", decoder=datetime.fromisoformat)
    )
    uid: str
    user_email: str
    user_status: str
    user_uid: str
    utility: str
    customer_signature: Optional[Dict[str, str]] = None
    declined: Optional[datetime] = field(
        metadata=config(field_name="declined", decoder=datetime.fromisoformat),
        default=None,
    )
    form_uid: Optional[str] = None
    meters: Optional[MetersListing] = None
    nickname: Optional[str] = None
    revoked: Optional[datetime] = field(
        metadata=config(field_name="revoked", decoder=datetime.fromisoformat),
        default=None,
    )
    template_uid: Optional[str] = None


@dataclass
class AuthorizationListing(DataClassJsonMixin):
    """Outermost representation of the Utilities Authorizations object."""

    authorizations: List[Authorization]
    next: Optional[str]
