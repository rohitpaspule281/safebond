import time
from collections import OrderedDict
from threading import Lock
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, *, max_size: int, ttl_seconds: int) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, tuple[float, T]] = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> T | None:
        now = time.time()
        with self._lock:
            record = self._store.get(key)
            if record is None:
                return None

            expires_at, value = record
            if expires_at < now:
                self._store.pop(key, None)
                return None

            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: T) -> None:
        expires_at = time.time() + self.ttl_seconds
        with self._lock:
            self._evict_expired_locked()
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)
            while len(self._store) > self.max_size:
                self._store.popitem(last=False)

    def _evict_expired_locked(self) -> None:
        now = time.time()
        expired_keys = [key for key, (expires_at, _) in self._store.items() if expires_at < now]
        for key in expired_keys:
            self._store.pop(key, None)
