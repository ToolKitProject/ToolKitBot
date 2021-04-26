from typing import Union

from aiogram import types as t
from libs.objects import Database

from . import UserText, Chat, User


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


async def chek(msg: t.Message):
    if await is_chat(msg) and not Database.get_chat(msg.chat.id):
        await Chat(chat=msg.chat)
    if not Database.get_user(msg.from_user.id):
        await User(user=msg.from_user)

    return False
