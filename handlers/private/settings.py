from time import time
from typing import *

from aiogram import types as t
from bot import dp
from libs.classes import User, is_private


@dp.message_handler(is_private, commands=["set"])
async def set(msg: t.Message):
    start = time()
    user: User = await User(user=msg.from_user)
    text = "Владеет\n"
    async for chat in user.get_owns():
        text += f"{chat.title}\n"
    end = time()
    text += f"Время выполнения {end-start} sec"
    await msg.reply(text)
