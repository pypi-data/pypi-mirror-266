"""A utility class for parsing and converting enum-like values."""
from __future__ import annotations

from enum import Enum
from typing import Type, TypeVar

from parsy import Parser, from_enum


T = TypeVar("T")


class ParseableEnum(Enum):
    """A utility class for parsing and converting enum-like values."""

    def __str__(self) -> str:
        """Overwrite string representation.

        Returns:
            A string of the value
        """
        return str(self.value)

    @classmethod
    def parser(cls) -> Parser:
        """Create a Parser object to convert enum-like values.

        Returns:
            A Parser object configured to parse enum-like values.
        """
        return from_enum(cls)

    @classmethod
    def parse(cls: Type[T], string: str) -> T:
        """Parse a string and convert it to an enum-like value.

        Parameters:
            string: The string to parse and convert.

        Returns:
            An enum-like value parsed from the input string.
        """
        return cls.parser().parse(string)  # type: ignore[attr-defined, no-any-return]
