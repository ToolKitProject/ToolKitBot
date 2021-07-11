from aiogram import types as t
from bot import bot, dp
from libs.classes import Errors as e
from libs import filters as f


@dp.message_handler(f.message.is_private, content_types=t.ContentType.ANY)
async def command(msg: t.Message):
    raise e.CommandNotFound(msg.from_user.language_code)
