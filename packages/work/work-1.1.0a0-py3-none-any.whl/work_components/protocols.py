"""Protocols (interfaces) for typing."""

from typing import Protocol

# pylint: disable=missing-function-docstring


class IFlags(Protocol):
    """Protocol of a `Flags` object."""

    def is_set(self, key: str) -> bool:
        ...

    def set(self, *flags: str) -> None:
        ...

    def remove(self, *flags: str) -> None:
        ...
