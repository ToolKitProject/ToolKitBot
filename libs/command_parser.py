from __future__ import annotations

import typing as p
from abc import ABC, abstractmethod

from aiogram import types as t

from bot import dp
from . import errors as e


class ParsedArgs:
    def __init__(self, **kwargs: str):
        self.expand(kwargs)

    def __getitem__(self, name):
        return self.get(name)

    def __getattr__(self, name):
        return None

    def __setitem__(self, key, value):
        self.add(key, value)

    def __setattr__(self, key, value):
        self.add(key, value)

    def __iter__(self):
        return self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def __bool__(self):
        return bool(len(self))

    def get(self, name) -> p.Optional["ParsedArgs"]:
        return self.__dict__[name] if name in self.__dict__ else None

    def items(self) -> p.ItemsView[str, "ParsedArgs"]:
        return self.__dict__.items()

    def keys(self) -> p.KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> p.ValuesView["ParsedArgs"]:
        return self.__dict__.values()

    def expand(self, items: dict[str, p.Any]):
        for key, value in items.items():
            self.add(key, value)

    def add(self, key: str, value: p.Any):
        if value is not None:
            self.__dict__[key] = value


class ParseObj:
    def __init__(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User | None = None):
        self.text = text
        self.entities = entities
        self.reply_user = reply_user

    def find(self, regexp: p.Pattern):
        matches = regexp.finditer(self.text)
        self.text = regexp.sub("", self.text)
        return list(matches)


class BaseArg(ABC):
    def __init__(self, dest: str, name: str, required: bool, default: p.Any | None = None):
        self.dest = dest
        self.name = name
        self.required = required
        self.default = default

    @abstractmethod
    async def parse(self, parse: ParseObj): ...

    @abstractmethod
    async def check(self, parse: ParseObj): ...


class BaseParser(ABC):
    args: list[BaseArg]

    def __init__(self):
        self.args = []

    def __call__(self, *filters, state=None):
        def wrapper(func):
            return self.set_action(*filters, func=func, state=state)

        return wrapper

    def add(self, *args: BaseArg):
        self.args += list(args)
        return self

    def set_action(self, *filters, func: p.Callable[[t.Message, ParsedArgs], p.Any], state=None):
        async def pre_handler(msg: t.Message):
            parsed = await self.parse_message(msg)
            await func(msg, parsed)

        filters = list(filters)
        filters.insert(0, self.filter)

        dp.register_message_handler(
            pre_handler,
            *filters,
            state=state
        )
        return pre_handler

    async def parse_message(self, msg: t.Message, chek: bool = True):
        ru = msg.reply_to_message.from_user if msg.reply_to_message else None
        return await self.parse(msg.text, msg.entities, ru, chek)

    @abstractmethod
    async def parse(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                    check: bool = True): ...

    @abstractmethod
    async def check(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                    err: bool = True): ...

    @abstractmethod
    async def check_all(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                        err: bool = False): ...

    @abstractmethod
    async def check_types(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                          err: bool = False, *types: str): ...

    @abstractmethod
    async def filter(self, msg: t.Message): ...


class BaseOrderParser(BaseParser, ABC):
    async def parse(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                    check: bool = True):
        items = ParsedArgs()
        parseOBJ = ParseObj(text, entities, reply_user)
        checkOBJ = ParseObj(text, entities, reply_user)

        if check:
            await self.check(text, entities, reply_user)

        for arg in self.args:
            if await arg.check(checkOBJ):
                try:
                    item = await arg.parse(parseOBJ)
                except Exception as err:
                    raise e.ArgumentError.ArgumentIncorrect(arg.name)
            else:
                item = arg.default

            items.add(arg.dest, item)
        return items

    async def check(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                    err: bool = True):
        obj = ParseObj(text, entities, reply_user)

        for arg in self.args:
            if arg.required:
                if not await arg.check(obj):
                    if err:
                        raise e.ArgumentError.ArgumentRequired(arg.name)
                    else:
                        return False
        return True

    async def check_all(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                        err: bool = False):
        obj = ParseObj(text, entities, reply_user)
        for arg in self.args:
            if not await arg.check(obj):
                if err:
                    raise e.ArgumentError.ArgumentRequired(arg.name)
                else:
                    return False
        return True

    async def check_types(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                          err: bool = False, *types: str):
        obj = ParseObj(text, entities, reply_user)
        for arg in self.args:
            if arg.dest in types:
                if not await arg.check(obj):
                    if err:
                        raise e.ArgumentError.ArgumentRequired(arg.name)
                    else:
                        return False
        return True


class BaseUnorderedParser(BaseParser, ABC):
    sep: str

    def __init__(self, sep=" "):
        super().__init__()
        self.sep = sep

    async def parse(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                    check: bool = True):
        pass

    async def check(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                    err: bool = True):
        pass

    async def check_all(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                        err: bool = False):
        pass

    async def check_types(self, text: str, entities: list[t.MessageEntity] = [], reply_user: t.User = None,
                          err: bool = False, *types: str):
        pass
