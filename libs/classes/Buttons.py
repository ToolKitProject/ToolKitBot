from copy import deepcopy
import typing as p

from aiogram import types as t
from bot import dp


class Menu(t.InlineKeyboardMarkup):
    title: str
    undo: bool = False
    storage: p.Dict[str, p.Any] = {}

    def __init__(self, title: str, row_width=3, inline_keyboard=None, undo: bool = False):
        super().__init__(row_width=row_width, inline_keyboard=inline_keyboard)
        self.title: str = title
        self.undo = undo

    async def send(self):
        from libs import src
        self = self.copy
        if self.undo:
            self.add(src.buttons.back)

        msg = t.Message.get_current()
        msg = await msg.answer(self.title, reply_markup=self)
        await self.save_storage(msg)
        return msg

    async def edit(self, save: bool = True):
        from libs import src
        self = self.copy
        if self.undo:
            self.add(src.buttons.back)

        msg = t.Message.get_current() or t.CallbackQuery.get_current().message
        await msg.edit_text(self.title, reply_markup=self)
        if save:
            await self.save_storage(msg)
        return msg

    async def save_storage(self, msg: t.Message):
        from libs.objects import MessageData
        with await MessageData.data(msg) as data:
            if not data.history:
                data.history = [self]
            else:
                data.history.append(self)

            for key, value in self.storage.items():
                data[key] = value

    def add(self, *args) -> "Menu":
        return super().add(*args)

    def row(self, *args):
        return super().row(*args)

    @property
    def copy(self):
        return deepcopy(self)


class Button(t.InlineKeyboardButton):
    def __init__(self, text: str, callback_data: str) -> None:
        super().__init__(text, callback_data=callback_data)

    def __call__(self, *filters, state=None):
        def wrapper(func):
            return self.set_handler(*filters, func=func, state=state)

        return wrapper

    def set_handler(self, *filters, func, state=None):
        filters = list(filters)
        filters.insert(0, self._filter)

        dp.register_callback_query_handler(
            func,
            *filters,
            state=state
        )
        return func

    def to_python(self) -> p.Dict[str, p.Any]:
        self.text = str(self.text)
        return super().to_python()

    @property
    def menu(self) -> t.InlineKeyboardMarkup:
        im = t.InlineKeyboardMarkup().add(self)
        return im

    async def _filter(self, clb: t.CallbackQuery):
        return str(self.callback_data) == str(clb.data)


class MenuButton(Button):
    def __init__(self, title: str, text: str, callback_data: str,
                 row_width=3, inline_keyboard=None, undo: bool = True, state=None):
        super().__init__(text=text, callback_data=callback_data)
        self.set_handler(self._filter, func=self.__handler, state=state)

        self.__menu = Menu(title=title, row_width=row_width, inline_keyboard=inline_keyboard, undo=undo)

    def add(self, *args):
        self.__menu.add(*args)
        return self

    def row(self, *args):
        self.__menu.add(*args)
        return self

    async def __handler(self, clb: t.CallbackQuery):
        await self.__menu.edit()
