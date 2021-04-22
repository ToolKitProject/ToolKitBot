from typing import *
from aiogram.types import *
from bot import dp
from libs.classes import UserText


def is_chat(msg: Union[CallbackQuery, Message]):
    if type(msg) == CallbackQuery:
        msg = msg.message
    return msg.chat.type in [ChatType.PRIVATE]


@dp.message_handler(is_chat, commands=["settings"])
async def get_menu(msg: Message):
    src = UserText(msg.from_user.language_code).buttons.private.settings
    await src.settings.answer(msg)
