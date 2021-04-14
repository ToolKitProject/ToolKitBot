import datetime
import asyncio
from typing import *

from aiogram import types
import aiogram
from aiogram.types import chat
from aiogram.types.chat import ChatType
from asyncinit import asyncinit
from bot import bot, client

from .Errors import *
from .Localisation import UserText


@asyncinit
class User:  # TODO:Добавить коментарии
    """
    Пользователь
    """

    async def __init__(self, user: types.User, chat: types.Chat):
        self.chat = chat
        self.user = user
        self.member = await chat.get_member(user.id)

        self.id = user.id
        self.username = user.username
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.lang = user.language_code
        self.bio = chat.bio

        return self

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
class Admin(User):
    """
    НЕ АДМИНИСТРОТОР, это админ команды
    """
    async def __init__(self, user: types.User, chat: types.Chat, creator: Optional[User] = None) -> None:
        await super().__init__(user, chat)

        self.creator: User = creator if creator else await User(user, chat)

    async def has_permission(self, action):
        member = await self.chat.get_member(self.creator.id)
        if action in ["ban", "unban", "kick", "mute", "unmute"]:
            perm = member.can_restrict_members

        if not (perm or member.is_chat_creator()):
            raise HasNotPermission(self.creator.lang)

    async def ban(self, until: datetime):
        await self.has_permission("ban")

        await self.chat.kick(self.id, until)

    async def unban(self):
        await self.has_permission("unban")

        await self.chat.unban(self.id, True)

    async def kick(self):
        await self.has_permission("kick")

        await self.chat.unban(self.id, False)

    async def mute(self, until: datetime):
        await self.has_permission("mute")

        perm = types.ChatPermissions(can_send_messages=False)
        await self.chat.restrict(self.id, perm, until)

    async def unmute(self):
        await self.has_permission("unmute")

        perm = types.ChatPermissions(
            True, True, True, True, True, True, True, True)
        await self.chat.restrict(self.id, perm)
