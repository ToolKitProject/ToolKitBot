import re

from aiogram import types as t

from bot import dp
from src import filters as f
from src.regex import regex as r
from libs import errors as e
from libs.chat import Chat


@dp.message_handler(f.message.is_chat, f.message.is_alias,
                    content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_executor(msg: t.Message):
    """
    Execute the alias as a new update
    """
    upd = t.Update.get_current()  # Get update obj
    chat = await Chat.create(msg.chat)  # Get chat obj
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
