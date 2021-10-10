import re

from aiogram import types as t

from bot import dp
from libs import errors as e
from src import filters as f
from src import regex as r
from src.utils import get_aliases, get_alias_text


@dp.message_handler(f.message.is_chat, f.message.is_alias,
                    content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_executor(msg: t.Message):
    """
    Execute the alias as a new update
    """
    upd = t.Update.get_current()

    aliases = get_aliases(msg)
    text = get_alias_text(msg)

    msg.sticker = None
    for key, value in aliases.items():
        pattern = re.compile(r.alias(key), re.IGNORECASE)
        if pattern.match(text):
            msg.text = pattern.sub(value + " ", text)

    upd.message = msg
    await dp.process_update(upd)


@dp.message_handler(f.message.is_private, content_types=t.ContentType.ANY)
async def command(msg: t.Message):  # If command not found
    await e.CommandNotFound().answer()
