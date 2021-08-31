import asyncio
import functools
import typing as p
from datetime import datetime, timedelta


def register_class(obj: p.Type, group: "CacheGroup"):
    @functools.wraps(obj.__new__)
    def new(cls: p.Type, *args, **kwargs):
        key = key_gen(args, kwargs)
        inst = group.get(key)
        if inst is None:
            cls.__init__(cls, *args, **kwargs)
            inst = group.add(cls, key)
        return inst

    obj.__new__ = new
    return obj


def register_callable(call: p.Callable, group: "CacheGroup"):
    if asyncio.iscoroutinefunction(call):
        @functools.wraps(call)
        async def new(*args, **kwargs):
            key = key_gen(args, kwargs)
            result = group.get(key)
            if result is None:
                result = group.add(await call(*args, **kwargs), key)
            return result
    else:
        @functools.wraps(call)
        def new(*args, **kwargs):
            key = key_gen(args, kwargs)
            result = group.get(key)
            if result is None:
                result = group.add(call(*args, **kwargs), key)
            return result

    return new


def key_gen(args, kwargs) -> str:
    return hash(args) + hash(tuple(kwargs.values()))


class Cache:
    _cache: p.Dict[str, "CacheGroup"]

    def __init__(self):
        self._cache = {}

    def register(self,
                 expires_delta: p.Optional[timedelta] = None,
                 expires_count: p.Optional[int] = None,
                 group_name: str = None):
        def wrapper(obj: p.Union[p.Type, p.Callable]):
            name = group_name or obj.__name__
            group = self.add(name, expires_delta, expires_count)

            if isinstance(obj, p.Type):
                return register_class(obj, group)
            elif isinstance(obj, p.Callable):
                return register_callable(obj, group)

        return wrapper

    def add(self,
            group_name: str,
            expires_delta: p.Optional[timedelta] = None,
            expires_count: p.Optional[int] = None) -> "CacheGroup":
        group = CacheGroup(expires_delta, expires_count)
        self._cache[group_name] = group
        return group

    def get(self, group_name: str) -> p.Optional["CacheGroup"]:
        if group_name in self._cache:
            return self._cache[group_name]
        return

    def expire(self, group_name: p.Optional[str] = None, hash: p.Optional[int] = None):
        if group_name:
            self._cache[group_name].expire(hash)
        else:
            for group in self._cache.values():
                group.expire()


class CacheGroup:
    _cache: p.Dict[int, "CachedObject"]

    expires_delta: timedelta
    expires_count: int

    def __init__(self, expires_delta: timedelta, expires_count: int):
        self._cache = {}

        self.expires_delta = expires_delta
        self.expires_count = expires_count

    def add(self, obj, hash: int) -> p.Any:
        cache = CachedObject(obj, self.expires_delta, self.expires_count)
        self._cache[hash] = cache
        return cache.cache

    def get(self, hash: int) -> p.Any:
        if hash in self._cache:
            return self._cache[hash].cache

    def expire(self, hash: p.Optional[int] = None):
        if hash:
            self._cache[hash].expire()
        else:
            for cache in self._cache.values():
                cache.expire()


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
