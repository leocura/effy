from __future__ import annotations
from typing import Callable, TypeVar, Sequence
from functools import reduce
from Effy._internal.fp import pure
from .types import Event

T = TypeVar("T")
S = TypeVar("S")

@pure
def filter_events(pred: Callable[[Event], bool], events: Sequence[Event]) -> tuple[Event, ...]:
    """Filter events based on a predicate."""
    return tuple(filter(pred, events))

@pure
def map_events(f: Callable[[Event], T], events: Sequence[Event]) -> tuple[T, ...]:
    """Map events to another type."""
    return tuple(map(f, events))

@pure
def fold_events(f: Callable[[S, Event], S], init: S, events: Sequence[Event]) -> S:
    """Fold (reduce) events into a state."""
    return reduce(f, events, init)
