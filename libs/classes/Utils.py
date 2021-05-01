import re
from typing import Dict, Text, Tuple, Union

from aiogram import types as t
from libs.objects import Database

from . import Chat, User, UserText


async def get_help(msg: t.Message):
    """
    Отправка help текста нужной локализации
    """
    if msg.get_command() != msg.text:
        return False
    command = msg.get_command(True)
    src = UserText(msg.from_user.language_code)
    await msg.reply(getattr(src.text.help, command), disable_web_page_preview=True)
    return True


async def is_chat(msg: Union[t.CallbackQuery, t.Message]):
    if type(msg) == t.CallbackQuery:
        msg = msg.message
    return msg.chat.type in [t.ChatType.GROUP, t.ChatType.SUPERGROUP]


async def is_private(msg: Union[t.CallbackQuery, t.Message]):
    if type(msg) == t.CallbackQuery:
        msg = msg.message
    return msg.chat.type in [t.ChatType.PRIVATE]


def clb(data):
    pattern = re.compile(data)

    async def filter(clb: t.CallbackQuery):
        if pattern.match(clb.data):
            return True
        return False
    return filter


async def alias(msg: t.Message, handler=True) -> Union[bool, str]:
    chat: Chat = await Chat(chat=msg.chat)
    if msg.sticker and "sticker_alias" in chat.settings:
        text: str = msg.sticker.file_unique_id
        aliases: Dict[str, str] = chat.settings["sticker_alias"]
    elif msg.text and "command_alias" in chat.settings:
        text: str = msg.text
        aliases: Dict[str, str] = chat.settings["command_alias"]

    if handler:
        return text in aliases
    else:
        return aliases[text]


async def chek(msg: t.Message):
    if await is_chat(msg):
        await Chat(chat=msg.chat)
    if not Database.get_user(msg.from_user.id):
        await User(user=msg.from_user)

    return False
