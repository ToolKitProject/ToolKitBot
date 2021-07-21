from aiogram import types as t

from bot import dp
from libs import filters as f
from libs.classes.Localisation import UserText
from libs.src import any
from libs.classes import Errors as e


@dp.message_handler(f.message.is_private, commands=["start"])
async def start(msg: t.Message):
    """
    Start command handler
    """
    src = UserText()
    await msg.answer(src.text.private.start_text)
