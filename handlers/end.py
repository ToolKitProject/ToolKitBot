from dataclasses import is_dataclass
from aiogram import types as t
from bot import bot, dp
from libs.classes import Errors as e
from libs.classes.Utils import is_private


@dp.message_handler(is_private, content_types=t.ContentType.ANY)
async def command(msg: t.Message):
    raise e.CommandNotFound(msg.from_user.language_code)
