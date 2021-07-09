from aiogram import types as t

from bot import client
from libs import system
from libs.classes.Localisation import UserText
from libs.classes.Utils import is_chat, bot_has_permission as bhp, has_permission as hp, get_help
from libs.src import any
from asyncio import sleep


@any.command.PurgeParser(is_chat, get_help, bhp("can_delete_messages"), hp("can_delete_messages"))
async def purge(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    parsed = await src.any.command.PurgeParser.parse(msg)

    from_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id - 1
    to_id = from_id - parsed.number

    msgs = list(range(from_id, to_id, -1))
    await client.delete_messages(msg.chat.id, msgs)
    await msg.answer(
        src.text.chat.admin.purge.format(
            count=parsed.number
        ),
        reply_markup=system.delete_this.inline
    )
    await sleep(1)
    await msg.delete()
