import typing as p
from aiogram import types as t, Bot

from libs.locales import Text, UserText


class Commands:
    groups: list["Group"]

    def __init__(self):
        self.groups = []

    def __iter__(self) -> p.Iterable["Group"]:
        return iter(self.groups)

    def __format__(self, format_spec: str) -> str:
        text = ""
        for group in self:
            if group.commands:
                text += str(group)
        return text

    def __str__(self) -> str:
        return format(self)

    def add(self, *groups: "Group") -> "Commands":
        groups = list(groups)

        for group in groups:  # merge commands
            if group.scope == t.BotCommandScopeDefault():
                for g in groups:
                    if g.scope not in [t.BotCommandScopeAllChatAdministrators(), t.BotCommandScopeDefault(), None]:
                        g.commands = group.commands + g.commands
            if group.scope == t.BotCommandScopeAllGroupChats():
                for g in groups:  # find AllAdmins group
                    if g.scope == t.BotCommandScopeAllChatAdministrators():
                        g.commands = group.commands + g.commands
                        break

        self.groups = groups
        return self

    def get(self, command: str) -> p.Optional["Command"]:
        for group in self:
            cmd = group.get(command)
            if cmd:
                return cmd

    def get_group(self, scope: t.BotCommandScope | None = None):
        for group in self:
            if scope == group.scope:
                return group

    async def set(self):
        for group in self:
            if group.scope is not None:
                await group.set(self.lang)

    async def delete(self):
        for group in self:
            await group.delete(self.lang)

    @property
    def lang(self):
        src = UserText()
        return src.lang


class Group:
    scope: t.BotCommand | None
    commands: list["Command"]

    def __init__(self, scope: t.BotCommand | None = None):
        self.scope = scope

        self.commands = []

    def __iter__(self) -> p.Iterable["Command"]:
        return iter(self.commands)

    def __bool__(self):
        return bool(self.commands)

    def __format__(self, format_spec: str) -> str:
        text = "\n\n".join([format(c, format_spec) for c in self]) + "\n\n"
        return "" if text == "\n\n" else text

    def __str__(self) -> str:
        return format(self)

    def add(self, *commands: "Command") -> "Group":
        self.commands += list(commands)
        return self

    def get(self, command: str) -> p.Optional["Command"]:
        for cmd in self:
            if command == cmd.command:
                return cmd

    async def set(self, lang: str) -> bool:
        bot = Bot.get_current()
        lang = _l(lang)
        await self.delete(lang)
        return await bot.set_my_commands(self.bot_commands, self.scope, lang)

    async def delete(self, lang: str) -> bool:
        bot = Bot.get_current()
        lang = _l(lang)
        return await bot.delete_my_commands(self.scope, lang)

    @property
    def bot_commands(self) -> list[t.BotCommand]:
        return [c.bot_command for c in self]


class Hide(Group):
    def __init__(self):
        super().__init__()


class Default(Group):
    def __init__(self):
        scope = t.BotCommandScopeDefault()
        super().__init__(scope)


class Private(Group):
    def __init__(self):
        scope = t.BotCommandScopeAllPrivateChats()
        super().__init__(scope)


class AllAdmins(Group):
    def __init__(self):
        scope = t.BotCommandScopeAllChatAdministrators()
        super().__init__(scope)


class AllChat(Group):
    def __init__(self):
        scope = t.BotCommandScopeAllGroupChats()
        super().__init__(scope)


class Chat(Group):
    def __init__(self, chat_id: int):
        scope = t.BotCommandScopeChat(chat_id)
        super().__init__(scope)


class Admin(Group):
    def __init__(self, chat_id: int):
        scope = t.BotCommandScopeChatAdministrators(chat_id)
        super().__init__(scope)


class Member(Group):
    def __init__(self, chat_id: int, user_id: int):
        scope = t.BotCommandScopeChatMember(chat_id, user_id)
        super().__init__(scope)


class Command:
    command: str
    description: str
    _help: list[Text]
    sep: str

    def __init__(self, command: str, description: str, *help: str, sep: str = "\n"):
        self.command = command
        self.description = description
        self._help = list(help)

        self.sep = sep

    def __format__(self, format_spec: str) -> str:
        if not format_spec:
            format_spec = "/{command} - {description}:{help}"
        return format_spec.format(command=self.command, description=self.description, help=self.help)

    def __str__(self) -> str:
        return format(self)

    @property
    def bot_command(self) -> t.BotCommand:
        return t.BotCommand(str(self.command), str(self.description))

    @property
    def help(self):
        return self.sep + self.sep.join([str(h) for h in self._help])


def _l(lang: str):
    return None if lang in ["other"] else lang
