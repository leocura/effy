from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from collections.abc import Hashable
import concurrent.futures

from Effy._internal.result import Err, Result
from Effy._internal.effect import Effect
from Effy.error import EffyError
from Effy._internal.fp import pure

T = TypeVar('T')
K = TypeVar('K', bound=Hashable)

@dataclass(frozen=True, slots=True)
class AssetManager(Generic[K, T]):
    """Pure functional state machine managing assets in a Least-Recently-Used (LRU) cache.
    
    Attributes:
        max_size: Maximum number of assets to keep in memory.
        _keys: Tuple of keys representing access order (last is most recently used).
        _items: Immutable mapping of keys to loaded assets.
    """
    max_size: int = 64
    _keys: tuple[K, ...] = ()
    _items: frozenset[tuple[K, T]] = frozenset()

    @pure
    def get(self, key: K) -> tuple[AssetManager[K, T], T | None]:
        """Retrieve an asset if loaded, returning the asset and an updated manager (for LRU tracking)."""
        # Linear search in frozenset isn't O(1) but for small max_size it's fine.
        # Let's build a dict locally for O(1) lookup:
        items_dict = dict(self._items)
        if key not in items_dict:
            return self, None
            
        # Update LRU order
        new_keys = tuple(k for k in self._keys if k != key) + (key,)
        return AssetManager(self.max_size, new_keys, self._items), items_dict[key]

    @pure
    def insert(self, key: K, asset: T) -> AssetManager[K, T]:
        """Insert a newly loaded asset into the manager, evicting the oldest if over capacity."""
        items_dict = dict(self._items)
        items_dict[key] = asset
        
        new_keys = tuple(k for k in self._keys if k != key) + (key,)
        
        if len(new_keys) > self.max_size:
            evicted_key = new_keys[0]
            new_keys = new_keys[1:]
            del items_dict[evicted_key]
            
        return AssetManager(self.max_size, new_keys, frozenset(items_dict.items()))


# --- Imperative Shell Loaders ---

# We use a global thread pool executor for the imperative shell's background loads.
# This state exists solely within the impure shell space.
_ASSET_EXECUTOR: concurrent.futures.ThreadPoolExecutor | None = None

def _get_executor() -> concurrent.futures.ThreadPoolExecutor:
    global _ASSET_EXECUTOR
    if _ASSET_EXECUTOR is None:
        _ASSET_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="effy_asset_worker")
    return _ASSET_EXECUTOR

def load_asset_async(loader: Callable[[], Result[T, EffyError]]) -> Effect[Result[T, EffyError]]:
    """Create an Effect that submits the loader to a background thread pool and waits for completion.
    
    This Effect should be run by the imperative shell. Since running it blocks the shell thread 
    awaiting the future, the shell should typically batch these futures or use them during 
    scene initialization rather than in the active game loop.
    
    Args:
        loader: A thunk that loads the asset and returns a Result.
        
    Returns:
        An Effect representing the background loading process.
    """
    def _run() -> Result[T, EffyError]:
        executor = _get_executor()
        future = executor.submit(loader)
        try:
            # We block here, but only in the imperative shell layer when the Effect is .run()
            return future.result()
        except Exception as e:
            return Err(EffyError(-1, f"Async load failed: {e}"))
            
    return Effect(_run)

