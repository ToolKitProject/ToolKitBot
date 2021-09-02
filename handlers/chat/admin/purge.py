import logging
import typing as p
from asyncio import sleep
from datetime import datetime

from aiogram import types as t

from bot import client
from libs import filters as f, utils as u
from libs.classes.CommandParser import ParsedArgs
from libs.classes.User import User
from libs.objects import Database
from libs.src import any, buttons, text


@any.parsers.purge(
    f.message.is_chat,
    f.bot.has_permission("can_delete_messages"),
    f.user.has_permission("can_delete_messages"),
    u.write_action,
    u.get_help
)
async def purge(msg: t.Message, parsed: ParsedArgs):
    """
    Purge handler
    """
    from_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id - 1
    to_id = from_id - parsed.count

    message_ids = list(range(from_id, to_id, -1))  # Create a global delete list
    message_ids.append(msg.message_id)
    await execute(message_ids, msg.chat.id)

    await msg.answer(
        text.chat.admin.purge.format(
            count=parsed.count
        ),
        reply_markup=buttons.delete_this.menu
    )


@any.parsers.clear_history(
    f.message.is_chat,
    f.bot.has_permission("can_delete_messages"),
    f.user.has_permission("can_delete_messages"),
    u.write_action,
    u.get_help
)
async def clear_history(msg: t.Message, parsed: ParsedArgs):
    users: p.List[User] = parsed.target
    delta = parsed.time
    to_date = datetime.now()
    from_date = to_date - delta
    messages = []

    for user in users:
        messages += Database.get_messages_id(user.id, msg.chat.id, from_date, to_date)

    await execute(messages, msg.chat.id)

    await msg.answer(
        text.chat.admin.purge.format(
            count=len(messages)
        ),
        reply_markup=buttons.delete_this.menu)


async def execute(message_ids: p.List[int], chat_id: int):
    if not message_ids:
        return

    Database.delete_messages(chat_id, message_ids)
    for x in range(len(message_ids[::100])):
        current_ids = message_ids[x * 100:x * 100 + 100]  # Create a local delete list (MAX 100)
        try:
            await client.delete_messages(chat_id, current_ids)  # Purge messages
            await sleep(0.3)
        except Exception as e:
            logging.warning(f"Purge warning: {e.__class__.__name__}:{e.args[0]}")
