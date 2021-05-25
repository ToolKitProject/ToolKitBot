from json import dumps, loads
from typing import *

from aiogram import types as t
from asyncinit import asyncinit
from bot import bot
from libs.objects import Database


@asyncinit
class Chat:

    __database__ = [
        "settings", "owner"
    ]
    _init = False

    async def __init__(self, auth: Union[int, str, t.Chat]):
        if isinstance(auth, t.Chat):
            self.chat = auth
        else:
            self.chat = await bot.get_chat(auth)

        if self.chat.type not in [t.ChatType.GROUP, t.ChatType.SUPERGROUP]:
            ValueError("Чет не так")

        self.id: int = self.chat.id
        self.type: str = self.chat.type
        self.title: str = self.chat.title
        self.username: str = self.chat.username
        try:
            self.invite_link: str = await self.chat.get_url()
        except:
            self.invite_link = None
        self.owner = await self._owner()

        DB_chat = Database.get_chat(self.id)
        if not DB_chat:
            DB_chat = Database.add_chat(self.id, self.owner.id)

        self.settings = loads(DB_chat.settings)

        self._init = True

        if DB_chat.owner != self.owner.id:
            self.owner = self.owner

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__database__ and self._init:
            if name in ["settings"]:
                v = dumps(value)
            elif name in ["owner"]:
                v = value.id
            Database.run(
                f"UPDATE Chats SET {name}='{v}' WHERE id={self.id};"
            )
        self.__dict__[name] = value

    @property
    def mention(self):
        if self.username:
            return self.username
        else:
            return self.title

    @property
    def link(self):
        return f"<a href='{self.invite_link}'>{self.title}</a>"

    @property
    def ping(self):
        if self.username:
            return f"@{self.username}"
        else:
            return self.link

    @property
    def sticker_aliases(self) -> Dict[str, str]:
        if "sticker_alias" in self.settings:
            return self.settings["sticker_alias"]
        return {}

    @property
    def command_aliases(self) -> Dict[str, str]:
        if "command_alias" in self.settings:
            return self.settings["command_alias"]
        return {}

    async def _owner(self):
        from .User import User
        admins = await self.chat.get_administrators()
        for admin in admins:
            if admin.is_chat_creator():
                result: User = await User(admin.user)
                return result
