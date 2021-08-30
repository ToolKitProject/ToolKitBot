import typing as p
from datetime import datetime, timedelta


class Cache:
    _cache: p.Dict[str, "CacheGroup"]

    def __init__(self):
        self._cache = {}

    def register(self, expires_delta: p.Optional[timedelta] = None, expires_count: p.Optional[int] = None):
        def wrapper(cls: p.Type):
            name = cls.__name__
            cls.__new__ = self._new

            self._cache[name] = CacheGroup(expires_delta, expires_count)
            return cls

        return wrapper

    def _new(self, cls: p.Type, *args, **kwargs):
        group = self._cache[cls.__name__]
        inst = group.get(cls, args, kwargs)
        if not inst:
            cls.__init__(cls, *args, **kwargs)
            group.add(cls, args, kwargs)
            return cls
        return inst


class CacheGroup:
    _cache: p.Dict[str, "CachedObject"]

    expires_delta: timedelta
    expires_count: int

    def __init__(self, expires_delta: timedelta, expires_count: int):
        self._cache = {}

        self.expires_delta = expires_delta
        self.expires_count = expires_count

    def add(self, cache: p.Any, args: p.Tuple, kwargs: p.Dict) -> "CachedObject":
        key = getattr(cache, "cache_key")(*args, **kwargs)
        value = CachedObject(cache, self.expires_delta, self.expires_count)
        self._cache[key] = value
        return value

    def get(self, cache_type: p.Type, args: p.Tuple, kwargs: p.Dict) -> p.Optional[p.Any]:
        key = getattr(cache_type, "cache_key")(*args, **kwargs)

        if key in self._cache:
            cache = self._cache[key].cache
            if not cache:
                self._cache.pop(key)
            return cache
        return None


class CachedObject:
    _cache: p.Any
    _get_count: int
    _expired: bool

    expires_date: p.Optional[timedelta]
    expires_count: p.Optional[int]

    def __init__(self,
                 cache: p.Any,
                 expires_delta: p.Optional[timedelta] = None,
                 expires_count: p.Optional[int] = None):
        self._cache = cache
        self._get_count = 0
        self._expired = False

        self.expires_date = datetime.now() + expires_delta if expires_delta else expires_delta
        self.expires_count = expires_count

    def get(self):
        return self.cache

    def extend(self, extend_delta: p.Optional[timedelta] = None, extend_count: p.Optional[int] = None):
        if extend_delta and self.expires_date:
            self.expires_date += extend_delta
        if extend_count and self.expires_count:
            self.expires_count += extend_count

    def expire(self):
        self._expired = True

    @property
    def expired(self) -> bool:
        expired = self._expired
        if self.expires_count:
            expired = expired or self._get_count >= self.expires_count
        if self.expires_date:
            expired = expired or datetime.now() >= self.expires_date

        return expired

    @property
    def cache(self) -> p.Optional[p.Any]:
        if not self.expired:
            self._get_count += 1
            return self._cache
        return None

    @property
    def get_count(self):
        return self._get_count
