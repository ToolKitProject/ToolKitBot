from copy import deepcopy
from typing import *

from aiogram.types import InlineKeyboardMarkup as IM
from aiogram.types import InlineKeyboardButton as IB
from aiogram import types as t
from bot import dp

registered = []
count = 0


class Menu:
    def __init__(self, title: str, undo: bool = False, row: int = 1) -> None:
        self.buttons: List[Button] = []
        self.row: int = row
        self.undo = undo
        self.title: str = title

        self.storage = {}

    def add(self, *buttons):
        for btn in buttons:
            self.buttons.append(btn)
        return self

    async def send(self, msg: t.Message):
        msg = await msg.answer(self.title, reply_markup=self.menu)
        await self.save_storage(msg)
        return msg

    async def edit(self, msg: t.Message, save: bool = True):
        await msg.edit_text(self.title, reply_markup=self.menu)
        if save:
            await self.save_storage(msg)
        return msg

    async def save_storage(self, msg: t.Message):
        from libs.objects import MessageData
        with await MessageData.data(msg) as data:
            if "history" not in data:
                data.history = [self]
            else:
                data.history.append(self)

            for key, value in self.storage.items():
                data.set(key, value)

    @property
    def copy(self):
        return deepcopy(self)

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
        global count

        self.text: str = text
        self.data = data

    def __call__(self, *filters, state=None):
        def handler(func):
            self.set_action(*filters, func=func, state=state)

        return handler

    def set_action(self, *filters, func, state=None):
        filters = list(filters)
        filters.append(self._filter)

        dp.register_callback_query_handler(
            func,
            *filters,
            state=state
        )
        return func

    def set_menu(self, menu: Menu):
        global registered
        if self.data in registered:
            return
        else:
            registered.append(self.data)

        handler = self._send_menu(menu)
        dp.register_callback_query_handler(handler, self._filter)

    @property
    def button(self):
        ib = IB(self.text, callback_data=self.data)
        return ib

    @property
    def inline(self):
        im = IM().add(self.button)
        return im

    async def _filter(self, clb: t.CallbackQuery):
        return str(self.data) == str(clb.data)

    @staticmethod
    def _send_menu(menu: Menu):
        async def handler(clb: t.CallbackQuery):
            await menu.edit(clb.message)

        return handler


class MenuButton(Menu, Button):
    def __init__(self, text: str, title: str, data: str, undo: bool = True, row: int = 1, make_unique: bool = True):
        global count

        super().__init__(title, undo=undo, row=row)
        self.text = text
        self.data = f"{data}:{count}" if make_unique else data
        self.set_menu(self)

        count += 1 if make_unique else 0
