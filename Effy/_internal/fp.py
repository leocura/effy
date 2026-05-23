from __future__ import annotations
from typing import TypeVar, Callable, Any

T = TypeVar("T")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

_EVOLVE_SENTINEL = object()

def pure(fn: Callable[..., T]) -> Callable[..., T]:
    """Marker decorator. No-op at runtime. Signals referential transparency."""
    return fn

def identity(x: T) -> T:
    """Return x unchanged."""
    return x

def const(x: T) -> Callable[..., T]:
    """Return a function that always returns x."""
    return lambda *args, **kwargs: x

def flip(fn: Callable[[A, B], C]) -> Callable[[B, A], C]:
    """Swap first two arguments of fn."""
    return lambda b, a: fn(a, b)

def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Apply functions left-to-right: pipe(x, f, g) == g(f(x))"""
    result = value
    for fn in fns:
        result = fn(result)
    return result

def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose right-to-left: compose(f, g)(x) == f(g(x))"""
    def _compose(x: Any) -> Any:
        """Inner function executing right-to-left composition of fns."""
        result = x
        for fn in reversed(fns):
            result = fn(result)
        return result
    return _compose

def memoize(fn: Callable[..., T], maxsize: int = 256) -> Callable[..., T]:
    """Cache results of a pure function. Only use on @pure functions."""
    from collections import OrderedDict
    cache: OrderedDict[tuple[Any, ...], T] = OrderedDict()
    def memoized(*args: Any) -> T:
        """Inner wrapper verifying if arguments are already in cache."""
        if args in cache:
            cache.move_to_end(args)
            return cache[args]
        result = fn(*args)
        cache[args] = result
        if len(cache) > maxsize:
            cache.popitem(last=False)
        return result
    return memoized

def curry(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Return a curried version of fn. Works for positional arguments."""
    import functools
    
    @functools.wraps(fn)
    def curried(*args: Any, **kwargs: Any) -> Any:
        """Inner wrapper accumulating arguments to execute currying logic."""
        if len(args) >= fn.__code__.co_argcount:
            return fn(*args, **kwargs)
        return lambda *more_args: curried(*(args + more_args), **kwargs)
    return curried

def getrefcount(target: Any) -> int:
    """Get the reference count of target. Compatible with CPython.
    
    On standard CPython, it delegates to sys.getrefcount to enable high-performance
    in-place mutations for transient buffers.
    On PyPy, since reference counting is not supported by the tracing GC and stack-frame
    scanning is inherently unsafe (missing references inside collections and object attributes),
    this safely returns a large value (999) to force safe Copy-on-Write behavior.
    """
    import sys
    if hasattr(sys, "getrefcount"):
        return sys.getrefcount(target)
    return 999

