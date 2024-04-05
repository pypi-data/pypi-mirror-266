"""Classifiers for objects relating to bills."""
from enum import Enum

from parsy import Parser, from_enum

from utility_api.models.object_types.base_enum import ParseableEnum


class Unit(ParseableEnum):  # type: ignore[misc]
    """Units accompanying numeric values."""

    kwh = "kwh"
    kw = "kw"
    kva = "kva"
    kvar = "kvar"
    kvarh = "kvarh"
    therms = "therms"
    ccf = "ccf"
    mcf = "mcf"
    hcf = "hcf"
    gallons = "gallons"
    m3 = "m3"
    days = "days"
    months = "months"
    percent = "percent"
    poles = "poles"
    lamps = "lamps"
    currency = "currency"

    @classmethod
    def parser(cls) -> Parser:
        """Create a Parser from the enum by converting its members to lowercase strings.

        Returns:
            A Parser object with enum members converted to lowercase strings.
        """
        return from_enum(cls, str.lower)


class ChargeKind(Enum):
    """Possible categories utilities often use to classify line item charges."""

    delivery = "delivery"
    supply = "supply"
    other = "other"


class BucketType(Enum):
    """Universal names for time-of-use periods."""

    peak = "peak"
    off_peak = "off-peak"
    part_peak = "part-peak"
    super_peak = "super-peak"
    super_off_peak = "super-off-peak"
    other = "other"


class PowerItemType(Enum):
    """Universal identifiers for power items captured."""

    reactive_demand = "reactive_demand"
    reactive_usage = "reactive_usage"
    real_demand = "real_demand"
    apparent_demand = "apparent_demand"
    power_factor = "power_factor"
