from aiogram import types as t

from libs import filters as f
from .Localisation import UserText


async def get_help(msg: t.Message):
    if await f.message.is_reply.check(msg):
        return True
    if not msg.get_args():
        await write_action(msg)
        command = msg.get_command(True)
        src = UserText(msg.from_user.language_code)

        try:
            text = getattr(src.text.help, command)
            await msg.reply(text, disable_web_page_preview=True)
            return False
        except:
            pass
    return True


async def write_action(msg: t.Message):
    if isinstance(msg, t.CallbackQuery):
        msg = msg.message
    await msg.answer_chat_action(t.ChatActions.TYPING)
    return True
