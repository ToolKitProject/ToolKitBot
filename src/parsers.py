import re
from calendar import isleap, monthrange
from copy import deepcopy
from datetime import timedelta, datetime

from aiogram.dispatcher import filters as f

from bot import dp
from libs import errors as e
from libs.command_parser import *
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


class Command(BaseParser):
    def __init__(self, commands: p.Union[p.List[str], str], name: str):
        from src.regex import regex as r
        self.commands = commands
        self.name = name

        self.args: p.List[BaseArg] = []

        self.add(
            Arg(r.parse.command, self.name, "command", True)
        )
        super().__init__()

    def __call__(self, *filters, state=None):
        def wrapper(func):
            return self.set_action(*filters, func=func, state=state)

        return wrapper

    def add(self, *args: BaseArg):
        self.args += list(args)
        return self

    async def parse(self, msg: t.Message):
        items = ParsedArgs()
        parseOBJ = ParseObj(msg)
        chekJBJ = ParseObj(msg)

        await self.check(msg)

        for arg in self.args:
            if await arg.check(chekJBJ):
                try:
                    item = await arg.parse(parseOBJ)
                except Exception:
                    raise e.ArgumentError.ArgumentIncorrect(arg.name)
            else:
                item = arg.default

            items.add(arg.dest, item)
        return items

    async def check(self, msg: t.Message):
        obj = ParseObj(msg)

        for arg in self.args:
            if arg.required:
                if not await arg.check(obj):
                    raise e.ArgumentError.ArgumentRequired(arg.name)
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

    def set_action(self, *filters, func: p.Callable[[t.Message, ParsedArgs], p.Any], state=None):
        async def pre_handler(msg: t.Message):
            parsed = await self.parse(msg)
            await func(msg, parsed)

        filters = list(filters)
        filters.insert(0, self._filter)

        dp.register_message_handler(
            pre_handler,
            *filters,
            state=state
        )
        return pre_handler

    @property
    def _filter(self):
        return f.Command(self.commands)


class Arg(BaseArg):
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


class ReasonArg(BaseArg):
    def __init__(
            self,
            name: str,
            dest: str = "reason",
            required: bool = False,
            default: p.Optional[p.Any] = ""
    ):
        from src.regex import regex as r
        self.regexp = re.compile(r.parse.reason)
        super().__init__(dest, name, required, default)

    async def parse(self, parse: ParseObj):
        matches = await find(self.regexp, parse)

        reason = ""
        for match in matches:
            reason = match.group("raw")

        return reason

    async def check(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        for _ in matches:
            return True
        return False


class UserArg(BaseArg):
    def __init__(
            self,
            name: str,
            dest: str = "users",
            required: bool = True,
            default: p.Optional[p.Any] = []
    ):
        from src.regex import regex as r
        self.regexp = re.compile(r.parse.user)
        super().__init__(dest, name, required, default)

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

        return list(set(users))

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
    def __init__(
            self,
            name: str,
            dest: str = "date",
            required: bool = False,
            default: p.Optional[p.Any] = timedelta()
    ):
        from src.regex import regex as r
        super().__init__(dest, name, required, default)
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
    def __init__(
            self, name: str,
            dest: str = "text",
            sep: str = " ",
            required: bool = False,
            default: p.Optional[p.Any] = ""
    ):
        from src.regex import regex as r
        self.regexp = re.compile(r.parse.text)
        self.sep = sep
        super().__init__(dest, name, required, default)

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

        from src.regex import regex as r
        self.min = minimal
        self.max = maximal
        self.contain = contain
        self.func = func
        self.regexp = re.compile(r.parse.number)
        super().__init__(dest, name, required, default)

    async def parse(self, parse: ParseObj):
        matches = await find(self.regexp, parse)
        numbers = []
        for match in matches:
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
        matches = await find(self.regexp, parse)
        for _ in matches:
            return True
        return False


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
            item = await flag.parse(deepcopy(parse))
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
    def __init__(
            self,
            small: str,
            full: str,
            dest: str,
            name: str,
            required: bool = False
    ):
        from src.regex import regex as r
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


class ValueFlag(Flag):
    def __init__(
            self,
            small: str,
            full: str,
            dest: str,
            name: str,
            required: bool = False
    ):
        from src.regex import regex as r

        super().__init__(small, full, dest, name, required)
        self.regexp = re.compile(r.parse.value_flag)

    async def parse(self, parse: ParseObj):
        if not await super().parse(deepcopy(parse)):
            return False

        matches = await find(self.regexp, parse)
        result = None
        for match in matches:
            result = match.group("value")
        return result

    async def check(self, parse: ParseObj):
        return super().parse(parse)


async def find(regexp: re.Pattern, parse: ParseObj):
    matches = regexp.finditer(parse.text)
    parse.text = regexp.sub("", parse.text)
    return matches
