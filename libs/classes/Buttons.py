from typing import *

from aiogram.types import InlineKeyboardMarkup as IM
from aiogram.types import InlineKeyboardButton as IB
from aiogram import types as t
from bot import dp

registered = []


class Menu:
    def __init__(self, title: str, undo: bool = False, row: int = 1) -> None:
        self.buttons: List[Button] = []
        self.row: int = row
        self.undo = undo
        self.title: str = title

    def add(self, *buttons):
        for btn in buttons:
            self.buttons.append(btn)
        return self

    async def send(self, msg: t.Message):
        from libs.objects import MessageData

        m = await msg.answer(self.title, reply_markup=self.menu)
        with await MessageData.state(m) as data:
            data.history = [self]
        return m

    async def edit(self, msg: t.Message, save: bool = True):
        from libs.objects import MessageData

        text = self.title
        m = await msg.edit_text(text, reply_markup=self.menu)
        if save:
            with await MessageData.state(m) as data:
                if "history" not in data:
                    data.history = [self]
                else:
                    history: List[Menu] = data.history
                    history.append(self)

    @property
    def menu(self):
        from libs.src import system

        im = IM(self.row)
        buttons = [btn.button for btn in self.buttons]
        im.add(*buttons)
        if self.undo:
            im.row(system.back.button)

        return im


class Button:
    def __init__(self, text: str, data: str) -> None:
        self.text: str = text
        self.data = data
        self.middleware = None

    def set_action(self, *filters, state=None):
        filters = list(filters)
        filters.append(self._filter)

        def handler(func):
            dp.register_callback_query_handler(
                func,
                *filters,
                state=state
            )
            return func

        return handler

    def set_menu(self, menu: Menu):
        global registered
        if self.data in registered:
            return
        else:
            registered.append(self.data)

        handler = self._send_menu(menu)
        dp.register_callback_query_handler(handler, self._filter)

    def set_middleware(self):
        def middleware(func):
            self.middleware = func

        return middleware

    @property
    def button(self):
        ib = IB(self.text, callback_data=self.data)
        return ib

    @property
    def inline(self):
        im = IM().add(self.button)
        return im

    async def _filter(self, clb: t.CallbackQuery):
        if self.middleware:
            self.middleware(clb)

        return self.data == clb.data

    @staticmethod
    def _send_menu(menu: Menu):
        async def handler(clb: t.CallbackQuery):
            await menu.edit(clb.message)

        return handler

    __call__ = set_action


class MenuButton(Menu, Button):
    def __init__(self, text: str, title: str, data: str, undo: bool = True, row: int = 1) -> None:
        super().__init__(title, undo=undo, row=row)
        self.text = text
        self.data = data
        self.middleware = None
        self.set_menu(self)
