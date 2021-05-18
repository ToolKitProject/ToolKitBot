import datetime
from json import loads, dumps
from libs.classes.Localisation import UserText
from typing import *

from aiogram import types as t
from asyncinit import asyncinit
from bot import bot, client
from libs.objects import Database
from datetime import datetime

from .Errors import *


@asyncinit
class User:  # TODO:Добавить коментарии
    """
    Пользователь
    """
    __database__ = [
        "settings", "permission"
    ]
    _init = False

    async def __init__(self, auth: Union[str, int, t.User], chat: Optional[t.Chat] = None):
        if isinstance(auth, t.User):
            self.user = auth
        else:
            self.user = await client.get_users(auth)

        self.chat = chat if chat else await bot.get_chat(self.user.id)

        self.id: int = self.user.id
        self.username: str = self.user.username
        self.first_name: str = self.user.first_name
        self.last_name: str = self.user.last_name
        self.language_code: str = self.user.language_code
        self.lang: str = self.language_code
        self.src: UserText = UserText(self.lang)

        DB_user = Database.get_user(self.id)
        if not DB_user:
            DB_user = Database.add_user(self.id)

        self.settings: dict = loads(DB_user.settings)
        self.permission: dict = loads(DB_user.permission)
        self.owns = Database.get_owns(self.id)

        self._init = True

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__database__ and self._init:
            Database.run(
                f"UPDATE Users SET {name}='{dumps(value)}' WHERE id={self.id};"
            )
        self.__dict__[name] = value

    @property
    def full_name(self):
        result = self.first_name
        if self.last_name:
            result += f" {self.last_name}"
        return result

    @property
    def mention(self):
        if self.username:
            return self.username
        else:
            return self.full_name

    @property
    def link(self):
        return f"<a href='tg://user?id={self.id}'>{self.full_name}</a>"

    @property
    def ping(self):
        if self.username:
            return f"@{self.username}"
        else:
            return self.link

    async def iter_owns(self):
        from . import Chat
        for chat in self.owns:
            result: Chat = await Chat(chat.id)
            yield result

    async def get_owns(self):
        result = []
        async for chat in self.iter_owns():
            result.append(chat)
        return result

    async def send(self,
                   text: str,
                   parse_mode: Optional[str] = None,
                   entities: Optional[List[t.MessageEntity]] = None,
                   disable_web_page_preview: Optional[bool] = None,
                   disable_notification: Optional[bool] = None,
                   reply_to_message_id: Optional[int] = None,
                   allow_sending_without_reply: Optional[bool] = None,
                   reply_markup: Union[t.InlineKeyboardMarkup,
                                       t.ReplyKeyboardMarkup,
                                       t.ReplyKeyboardRemove,
                                       t.ForceReply, None] = None,
                   ):
        await bot.send_message(self.id,
                               text=text,
                               entities=entities,
                               parse_mode=parse_mode,
                               disable_web_page_preview=disable_web_page_preview,
                               disable_notification=disable_notification,
                               reply_to_message_id=reply_to_message_id,
                               allow_sending_without_reply=allow_sending_without_reply,
                               reply_markup=reply_markup,)

    async def ban(self, until: Optional[datetime] = None, delete_all_messages: bool = False, revoke_admin: bool = False):
        if revoke_admin:
            await self.revoke_admin()
        await self.chat.kick(self.id, until, revoke_messages=delete_all_messages)

    async def unban(self):
        await self.chat.unban(self.id, True)

    async def kick(self, delete_all_messages: bool = False, revoke_admin: bool = False):
        if revoke_admin:
            await self.revoke_admin()
        await self.ban(delete_all_messages=delete_all_messages)
        await self.unban()

    async def mute(self, until: Optional[datetime] = None, revoke_admin: bool = False):
        if revoke_admin:
            await self.revoke_admin()
        perm = t.ChatPermissions(can_send_messages=False)
        await self.chat.restrict(self.id, perm, until)

    async def unmute(self):
        perm = t.ChatPermissions(
            True, True, True, True, True, True, True, True)
        await self.chat.restrict(self.id, perm)

    async def revoke_admin(self):
        await bot.promote_chat_member(
            self.chat.id,
            self.id,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False
        )

    async def has_permission(self, *permissions: str):
        member = await self.chat.get_member(self.id)
        for perm in permissions:
            if not (getattr(member, perm) or member.is_chat_creator()):
                return False
        return True
