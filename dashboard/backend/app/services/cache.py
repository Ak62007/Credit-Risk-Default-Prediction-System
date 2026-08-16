import threading
import time
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Minimal single-value cache with a time-to-live, refreshed lazily on access.

    Deliberately not a general-purpose keyed cache: this dashboard has a handful
    of expensive-to-recompute values (live prediction logs, the drift report),
    each with its own instance of this class. No Redis/Celery needed at this
    project's scale (single process, ~2k rows).
    """

    def __init__(self, loader: Callable[[], T], ttl_seconds: float | None):
        self._loader = loader
        self._ttl = ttl_seconds
        self._value: T | None = None
        self._loaded_at: float | None = None
        self._lock = threading.Lock()

    def get(self) -> T:
        with self._lock:
            expired = self._ttl is not None and (
                self._loaded_at is None or (time.monotonic() - self._loaded_at) > self._ttl
            )
            if self._value is None or expired:
                self._value = self._loader()
                self._loaded_at = time.monotonic()
            return self._value

    def loaded_at(self) -> float | None:
        return self._loaded_at

    def invalidate(self) -> None:
        with self._lock:
            self._value = None
            self._loaded_at = None
