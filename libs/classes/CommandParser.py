import re
import typing as p
from calendar import isleap, monthrange
from datetime import datetime, timedelta
from typing import List, Optional

from aiogram import types as t, filters as f
from asyncinit import asyncinit

from bot import dp
from libs.classes.Errors import ArgumentError, UserNotFound
from libs.src import system
from . import User, UserText


class dates:
    minimal = timedelta(seconds=30)
    maximal = timedelta(days=366)

    def forever(self, date: datetime):
        return \
            date < self.minimal or \
            date > self.maximal

    @property
    def now(self):
        return datetime.now()


CommandType = p.Union[p.List[str], str]
ArgType = p.Dict[str, p.Any]


class ParseArgs:
    def __init__(self, **kwargs: str):
        self.expand(kwargs)

    def __getitem__(self, name):
        return self.__dict__[name]

    def __setitem__(self, key, value):
        self.add(key, value)

    def __getattr__(self, name):
        return None

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

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def expand(self, items: ArgType):
        for key, value in items.items():
            self.add(key, value)

    def add(self, key: str, value: p.Any):
        if value:
            self.__dict__[key] = value


class BaseArg:
    def __init__(self, type: str, required: bool, default: p.Any):
        self.type = type
        self.required = required
        self.default = default

    def set_parser(self):
        def wrapper(parser: p.Coroutine):
            self.parse = parser

        return wrapper

    def set_checker(self):
        def wrapper(checker: p.Coroutine):
            self.check = checker

        return wrapper

    async def check(self, msg: t.Message):
        pass

    async def parse(self, msg: t.Message):
        items = ParseArgs()
        return items


class Command:
    def __init__(self, commands: CommandType, text: str, prefix: str = "/", separator: str = " "):
        self.commands = commands
        self.prefix = prefix
        self.separator = separator

        self.args: p.List[BaseArg] = []

    def __call__(self, *filters, state=None):
        def wrapper(func):
            return self.set_action(*filters, func=func, state=state)

        return wrapper

    def add(self, *args: BaseArg):
        self.args += list(args)

    async def check(self, parse: ParseArgs):
        pass

    async def parse(self, msg: t.Message):
        items = ParseArgs()
        for arg in self.args:
            item = await arg.parse(msg)
            items.add(arg.type, item)
        return items

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
        return f.Command(self.commands, self.prefix)


class Arg(BaseArg):
    def __init__(self, regexp: p.Union[re.Pattern, str], type: str, required: bool = True, default: p.Any = None):
        self.regexp = regexp if isinstance(regexp, re.Pattern) else re.compile(regexp)
        super().__init__(type, required=required, default=default)

    async def parse(self, msg: t.Message):
        items = ParseArgs()
        matches, msg.text = await self.match(msg.text)
        for match in matches:
            groups = match.groupdict()
            items.expand(groups)
        return items

    async def match(self, text: str):
        matches = self.regexp.finditer(text)
        text = self.regexp.sub("", text)
        return matches, text


class UserArg(BaseArg):
    def __init__(self):
        pass


class DateArg(BaseArg):
    def __init__(self):
        pass


class FlagsParser(BaseArg):
    def __init__(self):
        pass


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


@asyncinit
class AdminCommandParser:
    """
    Инструмент для парсинга команд
    """

    async def __init__(self, msg: t.Message, text: Optional[str] = None, target: Optional[User] = None) -> None:
        self.src = UserText(msg.from_user.language_code)

        self.msg = msg
        self.chat = msg.chat
        self.owner: User = await User(msg.from_user, chat=self.chat)

        self.text = text if text else msg.text
        self.entities = msg.entities

        self.cmd: str = None
        self.action: str = None
        self.bot: str = None

        self.targets: List[User] = [target] if target else []

        self.raw_date: str = None
        self.now: datetime = datetime.now()
        self.until: datetime = self.now

        self.flags = []
        self.revoke_admin = False
        self.delete_all_messages = False

        self.reason: str = ""

        await self.parse()
        await self.entities_parse()

        if not self.reason:
            self.reason = self.src.text.chat.admin.reason_empty
        if not self.targets or not self.cmd:
            raise ArgumentError(self.src.lang)

    async def parse(self):
        """
        Парс по regex
        """
        all = system.regex.parse.all.finditer(self.text)

        for match in all:
            group = match.lastgroup
            text: str = match.group(group)

            if group == "cmd":
                self.cmd = text
                self.bot = match.group("bot")
                self.action = match.group("action")
            elif group in ["id", "user"]:
                await self.to_user(text)
            elif group == "until":
                self.raw_date = text
                await self.to_date(match)
            elif group == "reason":
                self.reason += match.group("raw_reason")
            elif group == "flags":
                self.flags += list(text.replace("-", ""))

        self.delete_all_messages = "d" in self.flags
        self.revoke_admin = "r" in self.flags

        delta = self.until - self.now
        if (delta.total_seconds() < 30 or delta.days > 366) and self.until.timestamp() != self.now.timestamp():
            await self.msg.answer(self.src.text.errors.UntilWaring)
            # self.until = self.now

    @classmethod
    async def check(cls, text: str, *check: str):
        all = re.finditer(system.regex.parse.all, text)
        groups = []
        for math in all:
            groups.append(math.lastgroup)

        for c in check:
            if c in groups:
                return False
        return True

    async def entities_parse(self):
        """
        Парс по message entities
        """
        for entity in self.entities:
            if entity.type == "text_mention":
                user = await User(entity.user, chat=self.chat)
                self.targets.append(user)

    async def to_user(self, auth: str) -> User:
        """
        Преобразует упоминание в User
        """
        user = await User(auth, chat=self.chat)
        try:
            pass
        except Exception as e:
            raise UserNotFound(self.msg.from_user.language_code)
        self.targets.append(user)

    async def to_date(self, match: re.Match) -> int:
        """
        Преобразует строку в datetime
        """
        num: int = int(match.group("num"))
        datetype: str = match.group("type")

        if datetype == "s":
            delta = timedelta(seconds=num)
        elif datetype == "m":
            delta = timedelta(minutes=num)
        elif datetype == "h":
            delta = timedelta(hours=num)
        elif datetype == "d":
            delta = timedelta(days=num)
        elif datetype == "M":
            delta = timedelta(days=get_days_month(num, self.now))
        elif datetype == "y":
            delta = timedelta(days=get_days_years(num, self.now))

        self.until += + delta

    async def re_parse_date(self):
        if not self.raw_date:
            return
        self.now = datetime.now()
        self.until = self.now
        match = re.match(system.regex.parse.until, self.raw_date)
        await self.to_date(match)

    async def undo(self) -> str:
        if self.action.startswith("un"):
            return self.action.removeprefix("un")
        else:
            return "un" + self.action

    @property
    def format_until(self):
        """
        Возвращает форматированую дату
        """
        if self.now == self.until:
            return self.src.text.chat.admin.forever
        return f"{self.until.year}-{self.until.month}-{self.until.day}"

    @property
    def format_users(self):
        """
        Возвращает форматированных пользователей 
        """
        result = ""
        for user in self.targets:
            result += f"{user.link},"
        return result.removesuffix(",")
