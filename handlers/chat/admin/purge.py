from aiogram import types as t

from bot import dp
from libs.classes.Utils import is_chat, bot_has_permission, has_permission, get_help


@dp.message_handler(is_chat, get_help, bot_has_permission("can_delete_messages"), has_permission("can_delete_messages"),
                    commands=["purge"])
async def purge(msg: t.Message):
    pass
