from json import loads
import typing as p

from aiogram import types as t
from libs.classes.Localisation import UserText
from bot import dp
from libs.objects import Database

from .Buttons import Button, Menu, MenuButton
from .Chat import Chat
from .Message import Data
from libs.objects import MessageData

DictType = p.Dict[str, str]
ListType = p.List[str]
SettingsType = p.Dict[str, p.Union[ListType, DictType, str]]

#! i hate this file


class _List:
    def __init__(self, settings: ListType, lang: str) -> None:
        self.src = UserText(lang)
        self.lang = lang
        self.setting = settings

    def __iter__(self):
        return self.setting


class _Dict:
    def __init__(self, settings: SettingsType, lang: str) -> None:
        self.lang = lang
        self.src = UserText(lang)
        self.settings = settings

    @property
    def menu(self):
        return

    @property
    def items(self):
        return self.settings.items()

    @property
    def values(self) -> p.List[str]:
        return list(self.settings.values())

    @property
    def keys(self) -> p.List[str]:
        return list(self.settings.keys())

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.settings[key]
        elif isinstance(key, int):
            return self.settings[self.keys[key]]

    def __iter__(self):
        return self.settings


class _Alias:
    def __init__(self, lang: str, settings: DictType, text: str, data: str) -> None:
        self.src = UserText(lang)
        self.lang = lang
        self.settings = settings

        self.text = text
        self.data = data

    @property
    def delete_menu(self):
        s = self.src.buttons.private.settings
        menu = MenuButton(s.delete_text, s.delete_title,
                          f"delete@{self.data}", False, 2)

        delete_accept = Button(s.delete_accept, "delete_accept")

        @delete_accept.set_action()
        async def delete(clb: t.CallbackQuery):
            self.settings.pop(self.data)

        menu.add(
            delete_accept,
            Button(s.delete_cancel, "back")
        )

        return menu

    @property
    def edit_menu(self):
        pass

    @property
    def button(self):
        menu = MenuButton(self.text, f"{self.data} ➡ {self.text}", self.data)
        menu.add(
            self.delete_menu,
            # self.edit_menu
        )
        return menu


class DictSettings(_Dict):
    def __init__(self, settings: DictType, lang: str, data: str, text: str, title: str) -> None:
        super().__init__(settings, lang)

        self.data = data
        self.text = text
        self.title = title

    @property
    def menu(self):
        s = self.src.buttons.private.settings
        menu = MenuButton(self.text, self.title, self.data)

        add_alias = Button(s.add_alias, "add_alias")

        @add_alias.set_action()
        async def add(clb: t.CallbackQuery):
            await clb.answer("Не работет")

        menu.add(add_alias)
        for key, item in self.items:
            alias = _Alias(self.lang, self.settings, item, key)
            menu.add(alias.button)
        return menu


class ListSettings(_List):
    def __init__(self, settings: ListType, lang: str) -> None:
        super().__init__(settings, lang)


class ChatSettings(_Dict):
    @classmethod
    def get(cls, chat_id: int, lang: str):
        settings = ChatSettings(
            loads(Database.get_chat(chat_id).settings),
            lang
        )
        return settings

    def __init__(self, settings: SettingsType, lang: str) -> None:
        super().__init__(settings, lang)
        s = self.src.buttons.private.settings

        self.title = s.settings
        self.sticker_alias = DictSettings(self["sticker_alias"], lang, "sticker_alias",
                                          s.sticker_alias, s.alias_menu)
        self.command_alias = DictSettings(self["command_alias"], lang, "command_alias",
                                          s.command_alias, s.alias_menu)

    @property
    def menu(self):
        menu = Menu(self.title, False, row=2)
        menu.add(
            self.sticker_alias.menu,
            self.command_alias.menu
        )
        return menu

    async def send(self, msg: t.Message):
        return await self.menu.send(msg)
