from __future__ import annotations
import array
from typing import Dict, List


class PixelBufferPool:
    """A pool for recycling array frame-buffers to avoid GC churn.

    Not thread-safe by design: Effy's functional rendering pipeline is
    single-threaded per context. Removing the lock eliminates a mutex
    acquisition on every frame buffer get/put.
    """

    def __init__(self) -> None:
        """Initialize the PixelBufferPool with empty caches for arrays and zero-filled templates."""
        self._pool: Dict[tuple[int, int], List[array.array[int]]] = {}
        self._zeros: Dict[tuple[int, int], array.array[int]] = {}

    def get(self, width: int, height: int, zero: bool = False) -> array.array[int]:
        """Get a warm array matching dimensions from the pool, or allocate a new one.

        Args:
            width: Width of the buffer.
            height: Height of the buffer.
            zero: If True, ensures the returned buffer is zero-filled (transparent black).
        """
        key = (width, height)
        pool = self._pool.get(key)
        if pool:
            data = pool.pop()
            if zero:
                expected_size = width * height
                zero_bytes = self._zeros.get(key)
                if zero_bytes is None:
                    zero_bytes = array.array('I', [0] * expected_size)
                    self._zeros[key] = zero_bytes
                data[0:expected_size] = zero_bytes
            return data

        return array.array('I', [0] * (width * height))

    def put(self, width: int, height: int, data: array.array[int]) -> None:
        """Return the array back to the pool for reuse."""
        expected_size = width * height
        if len(data) != expected_size:
            return

        key = (width, height)
        pool = self._pool.get(key)
        if pool is None:
            self._pool[key] = [data]
        else:
            pool.append(data)


# Global pool singleton
pixel_buffer_pool = PixelBufferPool()
