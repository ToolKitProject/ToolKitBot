from aiogram import types as t

from bot import client
from libs import system
from libs.classes.Localisation import UserText
from libs.classes import Utils as u
from libs import filters as f
from libs.src import any
from asyncio import sleep


@any.command.PurgeParser(
    f.message.is_chat,
    f.bot.has_permission("can_delete_messages"),
    f.user.has_permission("can_delete_messages"),
    u.write_action,
    u.get_help
)
async def purge(msg: t.Message):
    """
    Purge handler
    """
    src = UserText(msg.from_user.language_code)
    parsed = await src.any.command.PurgeParser.parse(msg)  # Parse the message

    from_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id - 1
    to_id = from_id - parsed.number

    all_ids = list(range(from_id, to_id, -1))  # Create a global delete list
    for x in range(len(all_ids[::100])):
        current_ids = all_ids[x * 100:x * 100 + 100]  # Create a local delete list (MAX 100)
        try:
            await client.delete_messages(msg.chat.id, current_ids)  # Purge messages
        except:
            pass

    await msg.answer(
        src.text.chat.admin.purge.format(
            count=parsed.number
        ),
        reply_markup=system.delete_this.inline
    )
    await sleep(1)
    await msg.delete()
