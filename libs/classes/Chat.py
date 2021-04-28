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

    async def __init__(self, auth: str = None, chat: Optional[t.Chat] = None) -> None:
        self.chat = chat if chat else await bot.get_chat(auth)

        if self.chat.type not in [t.ChatType.GROUP, t.ChatType.SUPERGROUP]:
            ValueError("Чет не так")

        self.id: int = self.chat.id
        self.type: str = self.chat.type
        self.title: str = self.chat.title
        self.username: str = self.chat.username
        self.invite_link: str = self.chat.invite_link
        self.owner = await self._owner()

        DB_chat = Database.get_chat(self.id)
        if not DB_chat:
            Database.add_chat(self.id, self.owner.id)
            DB_chat = (self.id, "{}", self.owner.id)

        self.settings = loads(DB_chat[1])

        self._init = True

        if DB_chat[2] != self.owner.id:
            self.owner = self.owner

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__database__ and self._init:
            if name in ["settings"]:
                value = dumps(value)
            elif name in ["owner"]:
                value = value.id
            Database.run(
                f"UPDATE Chats SET {name}='{value}' WHERE id={self.id};"
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

    async def _owner(self):
        from .User import User
        admins = await self.chat.get_administrators()
        for admin in admins:
            if admin.is_chat_creator():
                result: User = await User(user=admin.user)
                return result
