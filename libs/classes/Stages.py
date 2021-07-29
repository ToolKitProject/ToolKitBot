import typing as p

from aiogram import types as t, Dispatcher, Bot
from aiogram.dispatcher.filters import state as s

from . import Commands as c
from libs import UserText


class StageGroup(s.StatesGroup):
    @classmethod
    async def next(cls) -> str:
        bot = Bot.get_current()
        chat = t.Chat.get_current()
        user = t.User.get_current()

        if chat.type == t.ChatType.PRIVATE:
            await bot.delete_my_commands(
                t.BotCommandScopeChat(user.id),
                t.User.get_current().language_code
            )

        await super().next()

    @classmethod
    async def finish(cls):
        from libs import system
        dp = Dispatcher.get_current()
        chat = t.Chat.get_current()

        if chat.type == t.ChatType.PRIVATE:
            await c.Chat(chat.id).delete("other")
            for l in system.langs:
                await c.Chat(chat.id).delete(l)

        await dp.current_state().finish()


class Stage(s.State):
    _commands: p.List[str] = []

    def __init__(self, commands: p.List[str] = [], state: p.Optional[str] = None, group_name: p.Optional[str] = None):
        self._commands = commands
        super().__init__(state, group_name)

    async def set(self):
        from libs import system
        chat = t.Chat.get_current()

        if chat.type == t.ChatType.PRIVATE:
            await self.commands.set("other")
            for l in system.langs:
                await self.commands.set(l)

        await super().set()

    @property
    def commands(self) -> c.Group:
        chat = t.Chat.get_current()
        src = UserText()
        commands = c.Chat(chat.id)
        for cmd in self._commands:
            commands.add(src.any.command_list.get(cmd))
        return commands
