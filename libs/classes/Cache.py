import typing as p
from datetime import datetime, timedelta


class Cache:
    _cache: p.Dict[str, "CacheGroup"]

    def __init__(self):
        self._cache = {}


class CacheGroup:
    _cache: p.Dict[str, "CachedObject"]

    unique_attr: str
    expires_delta: timedelta
    expires_count: int

    def __init__(self, unique_attr: str, expires_delta: timedelta, expires_count: int):
        self._cache = {}

        self.unique_attr = unique_attr
        self.expires_delta = expires_delta
        self.expires_count = expires_count

    def add(self, cache: p.Any) -> "CachedObject":
        key = getattr(cache, self.unique_attr)
        value = CachedObject(cache, self.expires_delta, self.expires_count)
        self._cache[key] = value
        return value

    def get(self, key: str) -> p.Any:
        pass


class CachedObject:
    _cache: p.Any
    _get_count: int
    _expired: bool

    expires_date: datetime
    expires_count: int

    def __init__(self, cache: p.Any, expires_delta: timedelta, expires_count: int):
        self._cache = cache
        self._get_count = 0
        self._expired = False

        self.expires_date = datetime.now() + expires_delta
        self.expires_count = expires_count

    def get(self):
        return self.cache

    def extend(self, extend_delta: p.Optional[timedelta] = None, extend_count: p.Optional[int] = None):
        if extend_delta:
            self.expires_date += extend_delta
        if extend_count:
            self.expires_count += extend_count

    def expire(self):
        self._expired = True

    @property
    def expired(self) -> bool:
        return (datetime.now() >= self.expires_date) or (self._get_count >= self.expires_count) or self._expired

    @property
    def cache(self) -> p.Optional[p.Any]:
        if not self.expired:
            self._get_count += 1
            return self._cache
        return None

    @property
    def get_count(self):
        return self._get_count
