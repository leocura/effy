from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Sequence

T = TypeVar("T", covariant=True)
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Effect(Generic[T]):
    """A lazy, composable description of a side-effectful computation."""

    _thunk: Callable[[], T]

    def run(self) -> T:
        """Execute the lazy effect computation.

        Returns:
            The result of the computed computation.
        """
        return self._thunk()

    def map(self, f: Callable[[T], U]) -> Effect[U]:
        """Apply a function to transform the result of this effect without executing.

        Args:
            f: The transformation function to apply.

        Returns:
            A new Effect representing the mapped computation.
        """
        thunk = self._thunk
        return Effect(lambda: f(thunk()))

    def and_then(self, f: Callable[[T], Effect[U]]) -> Effect[U]:
        """Chain another effectful computation depending on the result of this effect.

        Args:
            f: A function returning the next Effect to execute.

        Returns:
            A new Effect representing the composed computations.
        """
        thunk = self._thunk
        return Effect(lambda: f(thunk()).run())

    @staticmethod
    def pure(value: U) -> Effect[U]:
        """Lift a value into Effect without side effects.

        Args:
            value: The value to lift.

        Returns:
            A new Effect wrapping the value.
        """
        return Effect(lambda: value)

    @staticmethod
    def sequence(effects: Sequence[Effect[U]]) -> Effect[tuple[U, ...]]:
        """Batch independent effects into a single Effect returning a tuple of results.

        Args:
            effects: A sequence of Effect objects to evaluate.

        Returns:
            A single Effect wrapping the sequence results.
        """

        def _run() -> tuple[U, ...]:
            """Execute each effect sequentially and compile the results into a tuple."""
            return tuple(e.run() for e in effects)

        return Effect(_run)
