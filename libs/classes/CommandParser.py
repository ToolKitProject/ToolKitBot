import re
import typing as p
from abc import ABC, abstractmethod
from calendar import isleap, monthrange
from datetime import datetime, timedelta

from aiogram import types as t, filters as f

from bot import dp
from libs.system import regex as r
from . import Errors as e
from .User import User


class dates:
    minimal = timedelta(seconds=30)
    maximal = timedelta(days=366)

    @classmethod
    def forever(cls, date: timedelta):
        return \
            date < cls.minimal or \
            date > cls.maximal

    @staticmethod
    def now():
        return datetime.now()

    @classmethod
    def get_years(cls, years: int):
        days = 0
        now = cls.now()

        for y in range(now.year, now.year + years):
            year_days = 365
            if isleap(y):
                year_days += 1
            days += year_days
        return days

    @classmethod
    def get_month(cls, months: int):
        days = 0
        now = cls.now()

        for m in range(now.month, now.month + months):
            m = m % 12
            m = 1 if m == 0 else m
            days += monthrange(now.year, m)[1]
        return days


CommandType = p.Union[p.List[str], str]
ArgType = p.Dict[str, p.Any]


class _ParsedArgs:
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

        @rtype: p.Optional[_ParsedArgs]
        """
        return self.__dict__[name] if name in self.__dict__ else None

    def items(self):
        """

        @rtype: p.ItemsView[str, _ParsedArgs]
        """
        return self.__dict__.items()

    def keys(self):
        """

        @rtype: p.KeysView[str]
        """
        return self.__dict__.keys()

    def values(self):
        """

        @rtype: p.ValuesView[_ParsedArgs]
        """
        return self.__dict__.values()

    def expand(self, items: ArgType):
        for key, value in items.items():
            self.add(key, value)

    def add(self, key: str, value: p.Any):
        if value:
            self.__dict__[key] = value


class _ParseObj:
    def __init__(self, msg: t.Message):
        self.text = msg.text
        self.entities = msg.entities

        self.original_text = self.text


class BaseArg(ABC):
    def __init__(self, type: str, name: str, required: bool, default: p.Any = None):
        self.type = type
        self.name = name
        self.required = required
        self.default = default

    @abstractmethod
    async def parse(self, parse: _ParseObj):
        pass

    @abstractmethod
    async def check(self, parse: _ParseObj):
        pass


class Command:
    def __init__(self, commands: CommandType, name: str):
        self.commands = commands
        self.name = name

        self.args: p.List[BaseArg] = []

        self.add(
            Arg(r.parse.command, "command", self.name, True)
        )

    def __call__(self, *filters, state=None):
        def wrapper(func):
            return self.set_action(*filters, func=func, state=state)

        return wrapper

    def add(self, *args: BaseArg):
        self.args += list(args)
        return self

    async def parse(self, msg: t.Message):
        items = _ParsedArgs()
        obj = _ParseObj(msg)

        await self.check(msg)

        for arg in self.args:
            try:
                item = await arg.parse(obj)
            except:
                raise e.ArgumentError.ArgumentIncorrect(msg.from_user.language_code, arg.name)
            items.add(arg.type, item)
        return items

    async def check(self, msg: t.Message):
        obj = _ParseObj(msg)

        for arg in self.args:
            if arg.required:
                if not await arg.check(obj):
                    raise e.ArgumentError.ArgumentRequired(msg.from_user.language_code, arg.name)
        return True

    async def check_all(self, msg: t.Message):
        obj = _ParseObj(msg)
        for arg in self.args:
            if not await arg.check(obj):
                return False
        return True

    async def check_types(self, msg: t.Message, *types: str):
        obj = _ParseObj(msg)
        for arg in self.args:
            if arg.type in types:
                if not await arg.check(obj):
                    return False
        return True

    def set_action(self, *filters, func, state=None):
        filters = list(filters)
        filters.insert(0, self._filter)

        dp.register_message_handler(
            func,
            *filters,
            state=state
        )
        return func

    @property
    def _filter(self):
        return f.Command(self.commands)


class Arg(BaseArg):

    def __init__(self, regexp: p.Union[re.Pattern, str], type: str, name: str,
                 required: bool = True, default: p.Any = None):
        self.regexp = regexp if isinstance(regexp, re.Pattern) else re.compile(regexp)
        super().__init__(type, name, required=required, default=default)

    async def parse(self, parse: _ParseObj):
        items = _ParsedArgs()
        matches, parse.text = await self.match(parse.text)
        for match in matches:
            groups = match.groupdict()
            items.expand(groups)
        return items

    async def check(self, parse: t.Message):
        matches, parse.text = await self.match(parse.text)
        for _ in matches:
            return True
        return False

    async def match(self, text: str):
        matches = self.regexp.finditer(text)
        text = self.regexp.sub("", text)
        return matches, text


class UserArg(BaseArg):
    def __init__(self, name: str, required: bool = True, default: p.Any = None):
        super().__init__("user", name, required, default)

    async def parse(self, parse: _ParseObj):
        items = _ParsedArgs()
        users = []
        for e in parse.entities:
            type = e.type
            if type == "text_mention":
                users.append(await User.create(e.user))
            elif type == "mention":
                mention = e.get_text(parse.original_text)
                users.append(await User.create(mention))

        items.users = users
        return items

    async def check(self, parse: t.Message):
        for e in parse.entities:
            if e.type in ["text_mention", "mention"]:
                return True
        return False


class DateArg(BaseArg):
    def __init__(self, name: str, required: bool = False, default: p.Any = None):
        super().__init__("date", name, required, default)
        self.regexp = re.compile(r.parse.date)

    async def parse(self, parse: _ParseObj):
        items = _ParsedArgs()
        matches, parse.text = await self.match(parse.text)

        delta = timedelta()
        for match in matches:
            num, type = int(match.group("num")), match.group("type")
            if type == "s":
                delta += timedelta(seconds=num)
            elif type == "m":
                delta += timedelta(minutes=num)
            elif type == "h":
                delta += timedelta(hours=num)
            elif type == "d":
                delta += timedelta(days=num)
            elif type == "w":
                delta += timedelta(weeks=num)
            elif type == "M":
                delta += timedelta(days=dates.get_month(num))
            elif type == "y":
                delta += timedelta(days=dates.get_years(num))

        date = dates.now() + delta

        items.date = date if delta > timedelta() else None
        return items

    async def check(self, parse: _ParseObj):
        matches, parse.text = await self.match(parse.text)
        for _ in matches:
            return True
        return False

    async def match(self, text: str):
        matches = self.regexp.finditer(text)
        text = self.regexp.sub("", text)
        return matches, text


# Потом сделаю )))
class FlagsParser(BaseArg):
    def __init__(self, required: bool = False, default: p.Any = None):
        super().__init__("flags", required, default)


class Flag:
    def __init__(self):
        pass


class ValueFlag(Flag):
    def __init__(self):
        super().__init__()


def get_days_years(year: int, now: datetime):
    """
    Превращает года в дни
    """
    days = 0
    for y in range(now.year, now.year + year):
        year_days = 365
        if isleap(y):
            year_days += 1
        days += year_days
    return days


def get_days_month(month: int, now: datetime):
    """
    Превращает месяца в дни
    """
    days = 0
    years = month // 12
    month = month % 12

    for m in range(now.month, now.month + month):
        days += monthrange(now.year, m)[1]
    days += get_days_years(years, now)
    return days
