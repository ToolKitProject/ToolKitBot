import logging
import typing as p
from asyncio import sleep
from datetime import timedelta

from aiogram import types as t

from bot import client
from libs.command_parser import ParsedArgs
from libs.user import User 
from locales import other, text, buttons
from src import filters as f
from src import utils as u
from src.instances import Database


@other.parsers.purge(
    f.message.is_chat,
    f.bot.has_permission("can_delete_messages"),
    f.user.has_permission("can_delete_messages"),
    u.write_action,
    u.get_help
)
async def purge(msg: t.Message, parsed: ParsedArgs):
    from_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id - 1
    to_id = from_id - parsed.count

    message_ids = list(range(from_id, to_id, -1))
    message_ids.append(msg.message_id)

    await process_purge(message_ids)
    await msg.answer(
        text.chat.admin.purge.format(
            count=parsed.count
        ),
        reply_markup=buttons.delete_this.menu
    )


@other.parsers.clear_history(
    f.message.is_chat,
    f.bot.has_permission("can_delete_messages"),
    f.user.has_permission("can_delete_messages"),
    u.write_action,
    u.get_help
)
async def clear_history(msg: t.Message, parsed: ParsedArgs):
    parsed.targets: p.List[User]
    parsed.time: timedelta
    messages = []

    await u.raise_permissions_errors(parsed.targets, await msg.chat.get_administrators())
    if parsed.targets:
        for user in parsed.targets:
            messages += [
                m.message_id for m in
                Database.get_messages(user_id=user.id, chat_id=msg.chat.id, delta=parsed.time)
            ]

        await process_purge(messages)
        await msg.answer(
            text.chat.admin.purge.format(
                count=len(messages)
            ),
            reply_markup=buttons.delete_this.menu
        )


async def process_purge(message_ids: p.List[int]):
    if not message_ids:
        return
    chat_id = t.Chat.get_current().id

    Database.disable_autocommit()
    for id in message_ids:
        Database.delete_messages(chat_id=chat_id, message_id=id)
    Database.enable_autocommit()

    for ids in u.break_list_by_step(message_ids, 100):
        try:
            await client.delete_messages(chat_id, ids)
            await sleep(0.3)
        except Exception as e:
            logging.warning(f"Purge warning: {e.__class__.__name__}:{e.args[0]}")
