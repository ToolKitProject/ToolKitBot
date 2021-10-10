import re
import typing as p
from calendar import isleap, monthrange
from copy import deepcopy
from datetime import timedelta, datetime

from aiogram import types as t
from aiogram.dispatcher import filters as f

from libs.command_parser import BaseParser, BaseArg, ParseObj, ParsedArgs
from libs.user import User


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


class CommandParser(BaseParser):
    def __init__(self, commands: p.Union[p.List[str], str], name: str):
        super().__init__()
        self.commands = commands
        self.add(CommandArg(name))

    async def filter(self, msg: t.Message):
        return await f.Command(self.commands).check(msg)


class TextParser(BaseParser):
    def __init__(self):
        super().__init__()

    async def filter(self, msg: t.Message):
        return True


class ReArg(BaseArg):
    def __init__(
            self,
            regexp: p.Union[re.Pattern, str],
            name: str,
            dest: str,
            required: bool = True,
            default: p.Optional[p.Any] = None
    ):
        self.regexp = regexp if isinstance(regexp, re.Pattern) else re.compile(regexp)
        super().__init__(dest, name, required=required, default=default)

    async def parse(self, parse: ParseObj):
        items = ParsedArgs()
        for match in parse.find(self.regexp):
            groups = match.groupdict()
            items.expand(groups)
        return items

    async def check(self, parse: ParseObj):
        return bool(parse.find(self.regexp))


class CommandArg(BaseArg):
    def __init__(self, name: str, dest: str = "command", required: bool = True):
        from src import regex as r
        self.regexp = re.compile(r.parse.command)
        super().__init__(dest, name, required)

    async def parse(self, parse: ParseObj):
        items = ParsedArgs()

        for match in parse.find(self.regexp):
            items.full = match.group("full")
            items.text = match.group("text")
            items.bot = match.group("bot")

        return items

    async def check(self, parse: ParseObj):
        return bool(parse.find(self.regexp))


class ReasonArg(BaseArg):
    def __init__(
            self,
            name: str,
            dest: str = "reason",
            required: bool = False,
            default: p.Optional[p.Any] = ""
    ):
        from . import regex as r
        self.regexp = re.compile(r.parse.reason)
        super().__init__(dest, name, required, default)

    async def parse(self, parse: ParseObj):
        reason = ""
        for match in parse.find(self.regexp):
            reason = match.group("raw")

        return reason

    async def check(self, parse: ParseObj):
        return bool(parse.find(self.regexp))


class UserArg(BaseArg):
    def __init__(
            self,
            name: str,
            dest: str = "users",
            required: bool = True,
            default: p.Optional[p.Any] = []
    ):
        from . import regex as r
        self.regexp = re.compile(r.parse.user)
        super().__init__(dest, name, required, default)

    async def parse(self, parse: ParseObj):
        users = []
        if parse.reply_user:
            users.append(await User.create(parse.reply_user))
        for e in parse.entities:
            type = e.type
            try:
                if type == "text_mention":
                    users.append(await User.create(e.user))
            except Exception as e:
                pass
        for m in parse.find(self.regexp):
            users.append(await User.create(m.group("user")))

        return list(set(users))

    async def check(self, parse: ParseObj):
        if parse.reply_user:
            return True
        for e in parse.entities:
            if e.type in ["text_mention"]:
                return True

        return bool(parse.find(self.regexp))


class DateArg(BaseArg):
    def __init__(
            self,
            name: str,
            dest: str = "date",
            minimum: timedelta = None,
            maximum: timedelta = None,
            required: bool = False,
            default: p.Optional[p.Any] = timedelta()
    ):
        from . import regex as r
        super().__init__(dest, name, required, default)
        self.regexp = re.compile(r.parse.date)
        self.minimum = minimum
        self.maximum = maximum

    async def parse(self, parse: ParseObj):
        delta = timedelta()
        for match in parse.find(self.regexp):
            num, type = int(match.group("num")), match.group("type")

            if num > 1000:
                raise RuntimeError()

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

        if self.maximum and delta > self.maximum:
            raise RuntimeError()
        if self.minimum and delta < self.minimum:
            raise RuntimeError()

        return delta

    async def check(self, parse: ParseObj):
        return bool(parse.find(self.regexp))


class TextArg(BaseArg):
    def __init__(
            self, name: str,
            dest: str = "text",
            sep: str = " ",
            required: bool = False,
            default: p.Optional[p.Any] = ""
    ):
        from . import regex as r
        self.regexp = re.compile(r.parse.text)
        self.sep = sep
        super().__init__(dest, name, required, default)

    async def parse(self, parse: ParseObj):
        texts = []
        for match in parse.find(self.regexp):
            texts.append(match.group())
        return self.sep.join(texts)

    async def check(self, parse: ParseObj):
        return bool(parse.find(self.regexp))


class NumberArg(BaseArg):
    def __init__(
            self, name: str,
            minimal: p.Optional[int] = None,
            maximal: p.Optional[int] = None,
            contain: bool = True,
            dest: str = "number",
            func: p.Callable[[p.List[int]], int] = sum,
            required: bool = False,
            default: p.Optional[p.Any] = 0
    ):

        from . import regex as r
        self.min = minimal
        self.max = maximal
        self.contain = contain
        self.func = func
        self.regexp = re.compile(r.parse.number)
        super().__init__(dest, name, required, default)

    async def parse(self, parse: ParseObj):
        numbers = []
        for match in parse.find(self.regexp):
            numbers.append(int(match.group()))

        num = self.func(numbers)
        if self.min and self.max:
            if self.contain:
                assert self.min <= num <= self.max
            else:
                assert self.min < num < self.max
        elif self.min:
            if self.contain:
                assert self.min <= num
            else:
                assert self.min < num
        elif self.max:
            if self.contain:
                assert num <= self.max
            else:
                assert num < self.max

        return num

    async def check(self, parse: ParseObj):
        return bool(parse.find(self.regexp))


class FlagArg(BaseArg):
    def __init__(self, dest: str = "flags"):
        self.flags: p.List[Flag] = []
        super().__init__(dest, None, True, None)

    def add(self, *flags: BaseArg):
        self.flags += list(flags)
        return self

    async def parse(self, parse: ParseObj):
        items = ParsedArgs()
        for flag in self.flags:
            self.name = flag.name
            item = await flag.parse(deepcopy(parse))
            items.add(flag.dest, item)
        return items

    async def check(self, parse: ParseObj):
        for flag in self.flags:
            if flag.required:
                if not await flag.check(deepcopy(parse)):
                    self.name = flag.name
                    return False
        return True


class Flag(BaseArg):
    def __init__(
            self,
            small: str,
            full: str,
            dest: str,
            name: str,
            required: bool = False
    ):
        from . import regex as r
        assert len(small) == 1
        assert len(full) > 1

        self.small = small
        self.full = full

        self.regexp = re.compile(r.parse.flag)

        super().__init__(dest, name, required)

    async def parse(self, parse: ParseObj):
        for match in parse.find(self.regexp):
            prefix = match.group("prefix")
            text = match.group("text")

            if prefix in ["--", "—"]:
                return self.full == text
            elif prefix == "-":
                return self.small in text
        return False

    async def check(self, parse: ParseObj):
        return await self.parse(parse)


class ValueFlag(Flag):
    def __init__(
            self,
            small: str,
            full: str,
            dest: str,
            name: str,
            required: bool = False,
            default: p.Optional[None] = None,
            func: p.Optional[p.Callable[[str], p.Any]] = None
    ):
        from . import regex as r

        super().__init__(small, full, dest, name, required)
        self.regexp = re.compile(r.parse.value_flag)
        self.default = default
        self.func = func

    async def parse(self, parse: ParseObj) -> p.Any:
        if not await super().parse(deepcopy(parse)):
            return self.default

        result = None
        for match in parse.find(self.regexp):
            result = match.group("value")

        if self.func:
            return self.func(result)
        else:
            return result

    async def check(self, parse: ParseObj):
        return super().parse(parse)
