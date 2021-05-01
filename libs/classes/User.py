import datetime
from json import loads, dumps
from libs.classes.Localisation import UserText
from typing import *

from aiogram import types as t
from asyncinit import asyncinit
from bot import bot, client
from libs.objects import Database

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

    async def __init__(self, auth: int = None, user: Optional[t.User] = None):
        self.user = user if user else await client.get_users(auth)

        self.id: int = self.user.id
        self.username: str = self.user.username
        self.first_name: str = self.user.first_name
        self.last_name: str = self.user.last_name
        self.language_code: str = self.user.language_code
        self.src: UserText = UserText(self.language_code)

        DB_user = Database.get_user(self.id)
        if not DB_user:
            # Database.run(f"INSERT INTO Users(id) VALUES ({self.id});")
            Database.add_user(self.id)
            DB_user = (self.id, "{}", "{}")

        self.settings: dict = loads(DB_user[1])
        self.permission: dict = loads(DB_user[2])
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
        for id in self.owns:
            result: Chat = await Chat(id)
            yield result

    async def get_owns(self):
        from . import Chat
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


@asyncinit
class AdminPanel(User):
    async def __init__(self, auth: int = None, user: Optional[t.User] = None, creator: t.User = None):
        await super().__init__(auth=auth, user=user)
        self.creator: User = await User(user=creator)
        self._init = False

    async def has_permission(self, action, chat: t.Chat):
        member = await chat.get_member(self.creator.id)
        if action in ["ban", "unban", "kick", "mute", "unmute"]:
            perm = member.can_restrict_members

        if not (perm or member.is_chat_creator()):
            raise HasNotPermission(self.creator.language_code)

    async def ban(self, until: datetime, chat: t.Chat):
        await self.has_permission("ban", chat)

        await chat.kick(self.id, until)

    async def unban(self, chat: t.Chat):
        await self.has_permission("unban", chat)

        await chat.unban(self.id, True)

    async def kick(self, chat: t.Chat):
        await self.has_permission("kick", chat)

        await chat.unban(self.id, False)

    async def mute(self, until: datetime, chat: t.Chat):
        await self.has_permission("mute", chat)

        perm = t.ChatPermissions(can_send_messages=False)
        await chat.restrict(self.id, perm, until)

    async def unmute(self, chat: t.Chat):
        await self.has_permission("unmute", chat)

        perm = t.ChatPermissions(
            True, True, True, True, True, True, True, True)
        await chat.restrict(self.id, perm)
