from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Sequence
from Effy._internal.fp import pure
from Effy.events.types import Event

@dataclass(frozen=True, slots=True)
class EventQueue:
    """A functional, persistent, immutable queue for buffering events.
    
    All operations are referentially transparent and return a new queue instance.
    """
    _events: tuple[Event, ...] = ()

    @staticmethod
    @pure
    def empty() -> EventQueue:
        """Create a new empty EventQueue."""
        return EventQueue()

    @pure
    def push(self, event: Event) -> EventQueue:
        """Push a single event onto the back of the queue, returning a new EventQueue."""
        return EventQueue(self._events + (event,))

    @pure
    def push_many(self, events: Sequence[Event]) -> EventQueue:
        """Push a sequence of events onto the back of the queue, returning a new EventQueue."""
        if not events:
            return self
        return EventQueue(self._events + tuple(events))

    @pure
    def pop(self) -> tuple[Event | None, EventQueue]:
        """Pop an event from the front of the queue.
        
        Returns a tuple of (popped_event, new_queue).
        If the queue is empty, returns (None, self).
        """
        if not self._events:
            return None, self
        return self._events[0], EventQueue(self._events[1:])

    @pure
    def peek(self) -> Event | None:
        """Peek at the front event of the queue without removing it."""
        if not self._events:
            return None
        return self._events[0]

    @pure
    def is_empty(self) -> bool:
        """Check if the queue has no events."""
        return len(self._events) == 0

    def __len__(self) -> int:
        """Return the total number of events buffered in this queue."""
        return len(self._events)

    @pure
    def __add__(self, other: tuple[Event, ...] | Event) -> EventQueue:
        """Concatenate one or more events to the end of the queue using the '+' operator."""
        if isinstance(other, tuple):
            return self.push_many(other)
        return self.push(other)

    def __getitem__(self, index: int | slice) -> Any:
        """Retrieve an event or a sliced sub-queue by index or range slice."""
        if isinstance(index, slice):
            return EventQueue(self._events[index])
        return self._events[index]
