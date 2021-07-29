from aiogram import types as t

from libs import filters as f
from libs import UserText


async def get_help(msg: t.Message):
    src = UserText()
    if await f.message.is_reply.check(msg):
        return True
    if not msg.get_args():
        await msg.reply(src.any.command_list.get(msg.get_command(True).removeprefix("/")),
                        disable_web_page_preview=True)
        return False
    return True


async def write_action(msg: t.Message):
    if isinstance(msg, t.CallbackQuery):
        msg = msg.message
    await msg.answer_chat_action(t.ChatActions.TYPING)
    return True
