from typing import *
from aiogram.types import *
from bot import dp
from libs.src.other.buttons import private
from libs.classes import User, Menu, Button


def is_chat(msg: Union[CallbackQuery, Message]):
    if type(msg) == CallbackQuery:
        msg = msg.message
    return msg.chat.type in [ChatType.PRIVATE]


@private.settings.alias.set_action(is_chat)
async def alias(clb: CallbackQuery):
    pass
