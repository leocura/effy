"""Functional Result type representation containing success (Ok) or failure (Err)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Any, Protocol, NoReturn

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


class ResultProto(Protocol[T, E]):
    """Protocol establishing a common interface for Ok and Err variants."""

    def is_ok(self) -> bool:
        """Check if the result is success (Ok)."""
        ...
    def is_err(self) -> bool:
        """Check if the result is failure (Err)."""
        ...
    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to transform the successful value, keeping Err unchanged."""
        ...
    def map_err(self, f: Callable[[E], F]) -> Result[T, F]:
        """Apply a function to transform the failure error value, keeping Ok unchanged."""
        ...
    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Bind another computation returning a Result to the successful value."""
        ...
    def unwrap(self) -> T:
        """Unwrap the successful value, raising ValueError if failure."""
        ...
    def unwrap_or(self, default: T) -> T:
        """Unwrap the successful value or return a default value if failure."""
        ...


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Represents a successful computation result containing a value."""

    value: T

    def map(self, f: Callable[[T], U]) -> Ok[U]:
        """Apply a function to the contained value of a success."""
        return Ok(f(self.value))

    def map_err(self, f: Callable[[Any], Any]) -> Ok[T]:
        """Return Ok unmodified since mapping errors does not apply to success."""
        return self

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Bind another computation function that returns a Result."""
        return f(self.value)

    def is_ok(self) -> bool:
        """Check if the result is success (Ok)."""
        return True

    def is_err(self) -> bool:
        """Check if the result is failure (Err)."""
        return False

    def unwrap(self) -> T:
        """Unwrap the successful value."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Unwrap the successful value, ignoring the default."""
        return self.value


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Represents a failed computation result containing an error."""

    error: E

    def map(self, f: Callable[[Any], Any]) -> Err[E]:
        """Return the Err unmodified since mapping does not apply to failures."""
        return self

    def map_err(self, f: Callable[[E], F]) -> Err[F]:
        """Apply a function to the contained error value of a failure."""
        return Err(f(self.error))

    def and_then(self, f: Callable[[Any], Any]) -> Err[E]:
        """Return the Err unmodified since chaining does not apply to failures."""
        return self

    def is_ok(self) -> bool:
        """Check if the result is success (Ok)."""
        return False

    def is_err(self) -> bool:
        """Check if the result is failure (Err)."""
        return True

    def unwrap(self) -> NoReturn:
        """Raise a ValueError since unwrap cannot succeed on an Err."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: U) -> U:
        """Return the default value since this is an Err."""
        return default


Result = Ok[T] | Err[E]
