from datetime import datetime, timedelta
from typing import Optional, Dict, TypeVar, Generic, TypedDict
import hashlib
import json

# Key type
K = TypeVar("K")
# Value type
V = TypeVar("V")


class CacheEntry(TypedDict):
    result: V
    datetime: datetime


class Cache(Generic[K, V]):
    def __init__(self, ttl_minutes: int):
        self._ttl_minutes = ttl_minutes
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: K) -> Optional[V]:
        hash_digest = self._get_unique_string(key)

        cached_entry = self._cache.get(hash_digest)
        if cached_entry and self._is_valid(cached_entry["datetime"]):
            return cached_entry["result"]
        return None

    def set(self, key: K, value: V) -> None:
        hash_digest = self._get_unique_string(key)
        self._cache[hash_digest] = CacheEntry(result=value, datetime=datetime.now())

    def _get_unique_string(self, key: K) -> str:
        if isinstance(key, str):
            return key
        hash_object = hashlib.md5(json.dumps(key, sort_keys=True).encode())
        return hash_object.hexdigest()

    def _is_valid(self, cache_datetime: datetime) -> bool:
        return (datetime.now() - cache_datetime) < timedelta(minutes=self._ttl_minutes)
