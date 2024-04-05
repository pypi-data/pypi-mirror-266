"""Classifiers for interval objects."""
from enum import Enum


class DataPointType(Enum):
    """The type of value represented by the datapoint."""

    fwd = "fwd"  # Forward usage, i.e. energy consumed from the grid
    net = "net"  # Net usage. Is aggregate if from multiple meters
    rev = "rev"  # Reverse usage, i.e. energy sent back into the grid
    gen = "gen"  # Generated energy, i.e. from an on-site solar array, etc.
    max = "max"  # Maximum value seen during an interval period
