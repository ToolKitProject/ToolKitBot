import typing as p
from abc import ABC, abstractmethod
from aiogram import types as t


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

    def get(self, name):
        """

        @rtype: p.Optional[ParsedArgs]
        """
        return self.__dict__[name] if name in self.__dict__ else None

    def items(self):
        """

        @rtype: p.ItemsView[str, ParsedArgs]
        """
        return self.__dict__.items()

    def keys(self):
        """

        @rtype: p.KeysView[str]
        """
        return self.__dict__.keys()

    def values(self):
        """

        @rtype: p.ValuesView[ParsedArgs]
        """
        return self.__dict__.values()

    def expand(self, items: p.Dict[str, p.Any]):
        for key, value in items.items():
            self.add(key, value)

    def add(self, key: str, value: p.Any):
        if value is not None:
            self.__dict__[key] = value


class ParseObj:
    def __init__(self, msg: t.Message):
        self.text = msg.text
        self.entities = msg.entities
        self.reply_user = msg.reply_to_message.from_user if msg.reply_to_message else None


class BaseArg(ABC):
    def __init__(self, dest: str, name: str, required: bool, default: p.Optional[p.Any] = None):
        self.dest = dest
        self.name = name
        self.required = required
        self.default = default

    @abstractmethod
    async def parse(self, parse: ParseObj):
        pass

    @abstractmethod
    async def check(self, parse: ParseObj):
        pass


class BaseParser(ABC):
    pass
