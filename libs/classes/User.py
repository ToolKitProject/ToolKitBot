import datetime
from json import loads, dumps
from typing import *

from aiogram import types
from asyncinit import asyncinit
from bot import bot, client
from libs.objects import Database
from pyrogram import types as ptypes

from .Errors import *


@asyncinit
class User:  # TODO:Добавить коментарии
    """
    Пользователь
    """
    __database__ = [
        "settings", "owns", "permission"
    ]
    _init = False

    async def __init__(self, auth: int):
        self.user = await client.get_users(auth)
        self.DB_user = Database.run(
            f"SELECT * FROM Users WHERE id = {self.user.id}", True)
        self.chat = await bot.get_chat(self.user.id)

        self.id = self.user.id
        self.username = self.user.username
        self.first_name = self.user.first_name
        self.last_name = self.user.last_name
        self.lang = self.user.language_code
        self.bio = self.chat.bio

        if not self.DB_user:
            Database.run(f"INSERT INTO Users(id) VALUES ({self.id});")
            self.DB_user = Database.run(
                f"SELECT * FROM Users WHERE id = {self.user.id}", True)

        self.settings: dict = loads(self.DB_user[1])
        self.owns: list = loads(self.DB_user[2])
        self.permission: dict = loads(self.DB_user[3])

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

    async def get_common_chats(self) -> List[ptypes.Chat]:
        return None

    async def send(self,
                   text: str,
                   parse_mode: Optional[str] = None,
                   entities: Optional[List[types.MessageEntity]] = None,
                   disable_web_page_preview: Optional[bool] = None,
                   disable_notification: Optional[bool] = None,
                   reply_to_message_id: Optional[int] = None,
                   allow_sending_without_reply: Optional[bool] = None,
                   reply_markup: Union[types.InlineKeyboardMarkup,
                                       types.ReplyKeyboardMarkup,
                                       types.ReplyKeyboardRemove,
                                       types.ForceReply, None] = None,
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
    async def __init__(self, auth: int, creator: Optional[User] = None):
        self.creator: User = creator if creator else await User(self.id)

        await super().__init__(auth)

    async def has_permission(self, action, chat: types.Chat):
        member = await chat.get_member(self.creator.id)
        if action in ["ban", "unban", "kick", "mute", "unmute"]:
            perm = member.can_restrict_members

        if not (perm or member.is_chat_creator()):
            raise HasNotPermission(self.creator.lang)

    async def ban(self, until: datetime, chat: types.Chat):
        await self.has_permission("ban", chat)

        await chat.kick(self.id, until)

    async def unban(self, chat: types.Chat):
        await self.has_permission("unban", chat)

        await chat.unban(self.id, True)

    async def kick(self, chat: types.Chat):
        await self.has_permission("kick", chat)

        await chat.unban(self.id, False)

    async def mute(self, until: datetime, chat: types.Chat):
        await self.has_permission("mute", chat)

        perm = types.ChatPermissions(can_send_messages=False)
        await chat.restrict(self.id, perm, until)

    async def unmute(self, chat: types.Chat):
        await self.has_permission("unmute", chat)

        perm = types.ChatPermissions(
            True, True, True, True, True, True, True, True)
        await chat.restrict(self.id, perm)
