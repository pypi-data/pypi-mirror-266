"""Classifiers for objects relating to meters."""
from enum import Enum


class FrequencyType(Enum):
    """Frequency on which to monitor the meter."""

    monthly = "monthly"
    weekly = "weekly"
    daily = "daily"
    off = "off"


class PrepayType(Enum):
    """Frequency of which ongoing monitoring is prepaid."""

    month_to_month = "month_to_month"
    prepay_yearly = "prepay_yearly"


class SupplierType(Enum):
    """The type of supplier."""

    cca = "cca"  # Energy is supplied by a CCA
    direct_access = "direct_access"  # Energy is purchased directly from an ESP
    third_party = "third_party"  # Energy is provided by some other third party supplier
