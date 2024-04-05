"""Represents the authorization form sent to utility customer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class Form(DataClassJsonMixin):
    """Authorization form that has been generated and can be submitted by a customer."""

    authorization_uid: Optional[str]
    created: str
    customer_email: str
    disabled: bool
    is_archived: bool
    scope: Dict[str, Any]
    template_uid: str
    uid: str
    updated: str
    url: str
    user_email: str
    user_uid: str
    utility: str
