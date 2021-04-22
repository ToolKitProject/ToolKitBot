from typing import *
from aiogram.types import CallbackQuery, Message, ChatType
from bot import dp
from libs.classes import User


def is_chat(msg: Union[CallbackQuery, Message]):
    if type(msg) == CallbackQuery:
        msg = msg.message
    return msg.chat.type in [ChatType.PRIVATE]


@dp.message_handler(is_chat, commands=["settings"])
async def get_menu(msg: Message):
    arg = msg.get_args().split()[0]
    user: User = await User(msg.from_user.id)
    user.settings = {arg: "Тест короч"}
    await msg.answer(f"-- {arg} --")
