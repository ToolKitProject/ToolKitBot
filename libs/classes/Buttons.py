from copy import deepcopy
import typing as p

from aiogram import types as t
from bot import dp


class Menu(t.InlineKeyboardMarkup):
    title: str
    undo: bool = False
    storage: p.Dict[str, p.Any]

    def __init__(self, title: str, row_width: int = 3, inline_keyboard=None, undo: bool = False):
        super().__init__(row_width=row_width, inline_keyboard=inline_keyboard)
        self.title: str = title
        self.undo = undo

        self.storage = {}

    def __deepcopy__(self, *args, **kwargs):
        return Menu(self.title, row_width=self.row_width, inline_keyboard=self.inline_keyboard, undo=self.undo)

    async def send(self):
        from libs import src
        menu = self.copy
        if self.undo:
            menu.row(src.buttons.back)

        msg = t.Message.get_current() or t.CallbackQuery.get_current().message
        msg = await msg.answer(self.title, reply_markup=menu)
        await self.save_storage(msg)
        return msg

    async def edit(self, save: bool = True):
        from libs import src
        menu = self.copy
        if self.undo:
            menu.row(src.buttons.back)

        msg = t.Message.get_current() or t.CallbackQuery.get_current().message
        await msg.edit_text(self.title, reply_markup=menu)
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
        super().add(*args)
        return self

    def row(self, *args) -> "Menu":
        super().row(*args)
        return self

    @property
    def copy(self):
        c = deepcopy(self)
        return c


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

    def to_python(self) -> p.Dict[str, p.Any]:  # I hate JSON serializer
        self.text, t = str(self.text), self.text
        r = super().to_python()
        self.text = t
        return r

    @property
    def menu(self) -> t.InlineKeyboardMarkup:
        im = t.InlineKeyboardMarkup().add(self)
        return im

    async def _filter(self, clb: t.CallbackQuery):
        return str(self.callback_data) == str(clb.data)


class Submenu(Button):
    def __init__(self, title: str, text: str, callback_data: str,
                 row_width: int = 3, inline_keyboard=None, undo: bool = True, state=None):
        super().__init__(text=text, callback_data=callback_data)
        self.set_handler(self._filter, func=self.__handler, state=state)

        self.__menu = Menu(title=title, row_width=row_width, inline_keyboard=inline_keyboard, undo=undo)
        self.storage = self.__menu.storage

    def add(self, *args):
        self.__menu.add(*args)
        return self

    def row(self, *args):
        self.__menu.add(*args)
        return self

    async def edit(self, save: bool = True):
        return await self.__menu.edit(save)

    async def send(self):
        return await self.__menu.send()

    async def __handler(self, clb: t.CallbackQuery):
        await self.__menu.edit()
