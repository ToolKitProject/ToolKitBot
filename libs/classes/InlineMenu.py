from typing import *

from aiogram.types import InlineKeyboardMarkup as IM
from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import *
from bot import dp

# TODO: Доделать классы
global id_button
id_button = 0


class Menu:
    def __init__(self, title: str, row: Optional[int] = None) -> None:
        self.buttons: List[Button] = []
        self.row: Optional[int] = row if row else 1
        self.title: str = title

    def add(self, *buttons):
        for btn in buttons:
            self.buttons.append(btn)
        return self

    async def answer(self, msg: Message):
        await msg.answer(self.title, reply_markup=self.menu)

    async def edit(self, msg: Message):
        await msg.edit_text(self.title, reply_markup=self.menu)

    @property
    def menu(self):
        im = IM(self.row)
        buttons = [btn.button for btn in self.buttons]
        im.add(*buttons)

        return im


class MenuButton(Menu):
    def __init__(self, text: str, title: str, row: Optional[int] = None) -> None:
        super().__init__(title, row=row)
        self.text = text

        global id_button
        self.data = str(id_button)
        id_button += 1

        self._button = Button(self.text, self.data)
        self._button.menu(self)

    @property
    def button(self):
        return self._button.button


class Button:
    def __init__(self, text: str, data: str) -> None:
        self.text: str = text
        self.data = data

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

    def menu(self, menu: Menu):
        hander = self._send_menu(menu)
        dp.register_callback_query_handler(hander, self._filter)

    @property
    def button(self):
        ib = IB(self.text, callback_data=self.data)
        return ib

    @property
    def inline(self):
        im = IM().add(self.button)
        return im

    def _filter(self, clb: CallbackQuery):
        return self.data == clb.data

    def _send_menu(self, menu: Menu):
        async def handler(clb: CallbackQuery):
            await clb.message.edit_text(menu.title, reply_markup=menu.menu)
        return handler
