from copy import deepcopy
import typing as p

from aiogram import types as t
from bot import dp


class Menu(t.InlineKeyboardMarkup):
    title: str
    undo: bool
    hide: bool
    storage: p.Dict[str, p.Any]

    def __init__(self, title: str, row_width: int = 3, inline_keyboard=None, undo: bool = False, hide: bool = False):
        super().__init__(row_width=row_width, inline_keyboard=inline_keyboard)
        self.title: str = title
        self.undo = undo
        self.hide = hide

        self.storage = {}

    def __deepcopy__(self, *args, **kwargs):
        return Menu(self.title, row_width=self.row_width, inline_keyboard=self.inline_keyboard, undo=self.undo)

    async def send(self, history: bool = True, msg: t.Message = None):
        from locales import buttons

        menu = self.copy
        if self.undo:
            menu.row(buttons.back)

        msg = msg or t.Message.get_current() or t.CallbackQuery.get_current().message
        msg = await msg.answer(self.title, reply_markup=menu)
        await self.save_storage(msg, history)
        return msg

    async def edit(self, history: bool = True, msg: t.Message = None):
        from locales import buttons

        menu = self.copy
        if self.undo:
            menu.row(buttons.back)

        msg = msg or t.Message.get_current() or t.CallbackQuery.get_current().message
        await msg.edit_text(self.title, reply_markup=menu)
        await self.save_storage(msg, history)
        return msg

    async def save_storage(self, msg: t.Message, history: bool = True):
        from src.instances import MessageData
        with MessageData.data(msg) as data:
            for key, value in self.storage.items():
                data[key] = value
                if not self.hide:
                    data.menu = self
            if history:
                if not data.history:
                    data.history = [self]
                else:
                    data.history.append(self)

    def add(self, *args) -> "Menu":
        super().add(*args)
        return self

    def row(self, *args) -> "Menu":
        super().row(*args)
        return self

    def update(self, menu: "Menu"):
        self.inline_keyboard = menu.inline_keyboard
        return self

    @property
    def copy(self):
        c = deepcopy(self)
        return c


class Button(t.InlineKeyboardButton):
    def __init__(self, text: str, callback_data: str = None, url: str = None) -> None:
        super().__init__(text, callback_data=callback_data, url=url)

    def __call__(self, *filters, state=None):
        def wrapper(func):
            return self.set_action(*filters, func=func, state=state)

        return wrapper

    def set_action(self, *filters, func, state=None):
        if not self.callback_data:
            raise TypeError("This button has no callback_data")

        filters = list(filters)
        filters.insert(0, self._filter)
        dp.register_callback_query_handler(
            func,
            *filters,
            state=state
        )
        return func

    @property
    def menu(self) -> t.InlineKeyboardMarkup:
        im = t.InlineKeyboardMarkup().add(self)
        return im

    async def _filter(self, clb: t.CallbackQuery):
        return str(self.callback_data) == str(clb.data)


class Submenu(Button):
    def __init__(self, title: str, text: str, callback_data: str,
                 row_width: int = 3, inline_keyboard=None, undo: bool = True, hide: bool = False, state=None):
        super().__init__(text=text, callback_data=callback_data)
        self.set_action(self._filter, func=self.__handler, state=state)

        self.__menu = Menu(title=title, row_width=row_width, inline_keyboard=inline_keyboard, undo=undo, hide=hide)
        self.storage = self.__menu.storage
        self.inline_keyboard = self.__menu.inline_keyboard

    def add(self, *args):
        self.__menu.add(*args)
        return self

    def row(self, *args):
        self.__menu.add(*args)
        return self

    def update(self, menu: "Menu"):
        self.__menu.update(menu)
        return self

    async def edit(self, history: bool = True, msg: t.Message = None):
        return await self.__menu.edit(history=history, msg=msg)

    async def send(self, history: bool = True, msg: t.Message = None):
        return await self.__menu.send(history=history, msg=msg)

    async def __handler(self, clb: t.CallbackQuery):
        await self.__menu.edit()
