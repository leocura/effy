from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class EffyError:
    """An immutable error container representing an Effy subsystem failure.

    Attributes:
        code: The error code returned by the underlying subsystem.
        message: The descriptive error message detailing the failure.
    """
    code: int
    message: str

    def __str__(self) -> str:
        """Return a formatted string representation of the error."""
        return f"EffyError({self.code}): {self.message}"


# Backward-compatible alias
SDLError = EffyError

