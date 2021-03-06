from aiogram import types as t

from bot import dp
from libs import errors as e
from libs.chat import Chat
from locales import text, buttons
from src import filters as f


@dp.message_handler(f.message.is_private, commands=["start"])
async def start(msg: t.Message):
    """
    Start command handler
    """
    if msg.get_args():
        type, *other = msg.get_args().split("_")
        if type == "chatsettings":
            await chat_settings(msg, int(other[0]))
    else:
        await msg.answer(text.private.start_text, disable_web_page_preview=True)


async def chat_settings(msg: t.Message, chat_id: int):
    chat = await Chat.create(chat_id)
    if chat.owner.id != msg.from_user.id:
        raise e.HasNotPermission()
    await buttons.private.settings.chat.settings.menu(chat.settings).send()
