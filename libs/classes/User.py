from typing import *

import config
from aiogram import types
from aiogram.types.chat import ChatType
from bot import bot
from libs import src
from libs.src import other as _src_type


class UserText:
    def __init__(self, lang: str) -> None:
        if lang in config.lang_support:
            self.lang = lang
        else:
            self.lang = "other"

        self.src: _src_type = getattr(src, self.lang)
        self.text = self.src.text
        self.buttons = self.src.buttons

    @property
    def encode_lang(self) -> str:
        return config.lang_encode[self.lang]


class User:

    def __init__(self, chat: types.Chat) -> None:
        if chat.type not in [ChatType.PRIVATE, 'bot']:
            raise ValueError("Это не приват чат придурок")

        self.chat = chat

        self.id = chat.id
        self.username = chat.username
        self.first_name = chat.first_name
        self.last_name = chat.last_name
        self.bio = chat.bio

    async def ban(self, chat_id: int, parser, *args):
        await bot.kick_chat_member(chat_id, self.id, parser.until)

    async def unban(self, chat_id: int, *args):
        await bot.unban_chat_member(chat_id, self.id, True)

    async def kick(self, chat_id: int, parser, *args):
        await self.ban(chat_id, parser)
        await self.unban(chat_id)

    async def mute(self, chat_id: int, parser, *args):
        perm = types.ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat_id, self.id, perm, parser.until)

    async def unmute(self, chat_id: int, *args):
        perm = types.ChatPermissions(
            True, True, True, True, True, True, True, True)
        await bot.restrict_chat_member(chat_id, self.id, perm)

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
