"""General types for Utilities API objects."""
from enum import Enum


class ServiceType(Enum):
    """Basic classification for a particular tariff."""

    res_electric = "res-electric"
    comm_electric = "comm-electric"
    electric = "electric"
    res_gas = "res-gas"
    comm_gas = "comm-gas"
    gas = "gas"
    res_water = "res-water"
    comm_water = "comm_water"
    water = "water"
    other = "other"
    unknown = "unknown"


class Status(Enum):
    """Authorization status."""

    pending = "pending"
    updated = "updated"
    errored = "errored"
