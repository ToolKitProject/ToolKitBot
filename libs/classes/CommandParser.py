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

    def expand(self, items: ArgType):
        for key, value in items.items():
            self.add(key, value)

    def add(self, key: str, value: p.Any):
        add = value == [] or \
              value == {} or \
              value is None
        if not add:
            self.__dict__[key] = value


class ParseObj:
    def __init__(self, msg: t.Message):
        self.lang = msg.from_user.language_code
        self.text = msg.text
        self.entities = msg.entities

        self.reply_user = msg.reply_to_message.from_user if msg.reply_to_message else None


class BaseArg(ABC):
    def __init__(self, dest: str, name: str, required: bool):
        self.dest = dest
        self.name = name
        self.required = required

    @abstractmethod
    async def parse(self, parse: ParseObj):
        pass

    @abstractmethod
    async def check(self, parse: ParseObj):
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
        items = ParsedArgs()
        obj = ParseObj(msg)

        await self.check(msg)

        for arg in self.args:
            try:
                item = await arg.parse(obj)
            except:
                raise e.ArgumentError.ArgumentIncorrect(msg.from_user.language_code, arg.name)
            items.add(arg.dest, item)
        return items

    async def check(self, msg: t.Message):
        obj = ParseObj(msg)

        for arg in self.args:
            if arg.required:
                if not await arg.check(obj):
                    raise e.ArgumentError.ArgumentRequired(msg.from_user.language_code, arg.name)
        return True

    async def check_all(self, msg: t.Message):
        obj = ParseObj(msg)
        for arg in self.args:
            if not await arg.check(obj):
                return False
        return True

    async def check_types(self, msg: t.Message, *types: str):
        obj = ParseObj(msg)
        for arg in self.args:
            if arg.dest in types:
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
    def __init__(self, regexp: p.Union[re.Pattern, str], dest: str, name: str, required: bool = True):
        self.regexp = regexp if isinstance(regexp, re.Pattern) else re.compile(regexp)
        super().__init__(dest, name, required=required)

    async def parse(self, parse: ParseObj):
        items = ParsedArgs()
        matches = await find(self.regexp, parse)
        for match in matches:
            groups = match.groupdict()
            items.expand(groups)
        return items

    async def check(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        for _ in matches:
            return True
        return False


class UserArg(BaseArg):
    def __init__(self, name: str, required: bool = True):
        self.regexp = re.compile(r.parse.user)
        super().__init__("user", name, required)

    async def parse(self, parse: ParseObj):
        users = []
        matches = await find(self.regexp, parse)

        if parse.reply_user:
            users.append(await User.create(parse.reply_user))
        for e in parse.entities:
            type = e.type
            if type == "text_mention":
                users.append(await User.create(e.user))
        for m in matches:
            users.append(await User.create(m.group("user")))

        return users

    async def check(self, parse: ParseObj):
        matches = await find(self.regexp, parse)

        if parse.reply_user:
            return True
        for e in parse.entities:
            if e.type in ["text_mention"]:
                return True
        for _ in matches:
            return True

        return False


class DateArg(BaseArg):
    def __init__(self, name: str, required: bool = False):
        super().__init__("date", name, required)
        self.regexp = re.compile(r.parse.date)

    async def parse(self, parse: ParseObj):
        matches = await find(self.regexp, parse)

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

        return delta

    async def check(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        for _ in matches:
            return True
        return False


class TextArg(BaseArg):
    def __init__(self, name: str, dest: str = "text", sep: str = " ", required: bool = False):
        self.regexp = re.compile(r.parse.text)
        self.sep = sep
        super().__init__(dest, name, required)

    async def parse(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        texts = []
        for match in matches:
            texts.append(match.group())
        return self.sep.join(texts)

    async def check(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        for _ in matches:
            return True
        return False


class NumberArg(BaseArg):
    def __init__(self, minimal: int, maximal: int, name: str, dest: str = "number",
                 func: p.Callable[[p.List[int]], int] = sum, required: bool = False):
        self.min = minimal
        self.max = maximal
        self.func = func
        self.regexp = re.compile(r.parse.number)
        super().__init__(dest, name, required)

    async def parse(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        numbers = []
        for match in matches:
            numbers.append(int(match.group()))

        num = self.func(numbers)
        if numbers and not (self.min <= num <= self.max):
            raise ValueError()
        return num

    async def check(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        for _ in matches:
            return True
        return False


class FlagArg(BaseArg):
    def __init__(self):
        self.flags: p.List[Flag] = []
        super().__init__("flags", None, True)

    def add(self, *flags: BaseArg):
        self.flags += list(flags)
        return self

    async def parse(self, parse: ParseObj):
        items = ParsedArgs()
        for flag in self.flags:
            item = await flag.parse(parse)
            items.add(flag.dest, item)
        return items

    async def check(self, parse: ParseObj):
        for flag in self.flags:
            if flag.required:
                if not await flag.check(parse):
                    self.name = flag.name
                    return False
        return True


class Flag(BaseArg):
    def __init__(self, small: str, full: str, dest: str, name: str, required: bool = False):
        assert len(small) == 1
        assert len(full) > 1

        self.small = small
        self.full = full

        self.regexp = re.compile(r.parse.flag)

        super().__init__(dest, name, required)

    async def parse(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        for match in matches:
            prefix = match.group("prefix")
            text = match.group("text")

            if prefix in ["--", "—"]:
                return self.full == text
            elif prefix == "-":
                return self.small in text
        return False

    async def check(self, parse: ParseObj):
        return await self.parse(parse)


# I will make later
class ValueFlags(Flag):
    def __init__(self):
        pass


async def find(regexp: re.Pattern, parse: ParseObj):
    matches = regexp.finditer(parse.text)
    parse.text = regexp.sub("", parse.text)
    return matches
