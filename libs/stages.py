import typing as p

from aiogram import types as t, Dispatcher, Bot
from aiogram.dispatcher.filters import state as s

from bot import dp
from . import commands as c
from locales import langs


class StageGroup(s.StatesGroup):
    def __call__(self, *filters):
        def wrapper(func):
            return self.set_action(*filters, func=func)

        return wrapper

    def set_action(self, *filters, func: p.Callable[[t.Message], p.Any]):
        dp.register_message_handler(
            func,
            *filters,
            state=self
        )
        return func

    @classmethod
    async def next(cls) -> str:
        raise RuntimeError("Use stage.set()")

    @classmethod
    async def finish(cls):
        dp = Dispatcher.get_current()
        chat = t.Chat.get_current()

        await dp.current_state().finish()

        if chat.type == t.ChatType.PRIVATE:
            await c.Chat(chat.id).delete("other")
            for l in langs:
                await c.Chat(chat.id).delete(l)


class Stage(s.State):
    _commands: p.List[str]
    text: p.Optional[str]

    def __init__(self,
                 commands: p.List[str] = [],
                 text: p.Optional[str] = None,
                 state: p.Optional[str] = None,
                 group_name: p.Optional[str] = None):
        self._commands = ["cancel"] + commands
        self.text = text
        super().__init__(state, group_name)

    def __call__(self, *filters, **kwargs):
        def wrapper(func):
            return self.set_action(*filters, func=func, **kwargs)

        return wrapper

    def set_action(self, *filters, func: p.Callable[[t.Message], p.Any], **kwargs):
        dp.register_message_handler(
            func,
            *filters,
            state=self,
            **kwargs
        )
        return func

    async def set(self):
        from config import langs
        chat = t.Chat.get_current()

        msg = t.Message.get_current()
        clb = t.CallbackQuery.get_current()
        if self.text:
            if msg:
                await msg.answer(self.text)
            elif clb:
                await clb.message.edit_text(self.text)
        async with dp.current_state().proxy() as data:
            if "_message" not in data:
                if msg:
                    data["_message"] = msg
                elif clb:
                    data["_message"] = clb.message

        await super().set()

        if chat.type == t.ChatType.PRIVATE:
            await self.commands.set("other")
            for l in langs:
                await self.commands.set(l)

    @property
    def commands(self) -> c.Group:
        from locales import other

        chat = t.Chat.get_current()
        commands = c.Chat(chat.id)
        for cmd in self._commands:
            commands.add(other.command_list.get(cmd))
        return commands
