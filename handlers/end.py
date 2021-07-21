import re

from aiogram import types as t

import handlers
from bot import dp
from libs import filters as f
from libs.system import regex as r
from libs.classes import Errors as e
from libs.classes.Chat import Chat


@dp.message_handler(f.message.is_chat, f.message.is_alias,
                    content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_executor(msg: t.Message):
    """
    Execute the alias as a new update
    """
    upd = t.Update.get_current()  # Get update obj
    chat = await Chat.create()  # Get chat obj
    text = None

    # Edit text
    if msg.sticker:
        text = chat.settings.sticker_alias[msg.sticker.file_unique_id]
        msg.sticker = None
    elif msg.text:
        aliases = chat.settings.text_alias
        for als, txt in aliases.items():
            pattern = re.compile(r.alias(als), re.IGNORECASE)
            if pattern.match(msg.text):
                text = pattern.sub(txt, msg.text)

    msg.text = text

    # Process update
    upd.message = msg
    await dp.process_update(upd)


@dp.message_handler(f.message.is_private, content_types=t.ContentType.ANY)
async def command(msg: t.Message):  # If command not found
    await e.CommandNotFound().answer()
    await handlers.all.fix_commands(msg, False)
