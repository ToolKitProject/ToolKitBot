from aiogram import types
from . import UserText


async def get_help(msg: types.Message):
    """
    Отправка help текста нужной локализации
    """
    if msg.get_command() != msg.text:
        return False
    command = msg.get_command(True)
    src = UserText(msg.from_user.language_code)
    await msg.reply(getattr(src.text.help, command), disable_web_page_preview=True)
    return True
