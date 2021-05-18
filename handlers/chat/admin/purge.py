from bot import client, dp
from libs.classes import Errors as e
from libs.classes import UserText
from aiogram import types as t
from libs.src import system
from libs.classes.Utils import is_chat, is_reply, bot_has_permission, has_permission, get_help, mark_write


@dp.message_handler(is_chat, get_help, bot_has_permission("can_delete_messages"), has_permission("can_delete_messages"),  commands=["purge"])
async def purge(msg: t.Message):
    await msg.delete()
    await mark_write(msg)

    src = UserText(msg.from_user.language_code)
    args = msg.get_args().split()
    count = int(args[0])

    if await is_reply.check(msg):
        from_id = msg.reply_to_message.message_id
    else:
        from_id = msg.message_id - 1

    try:
        assert count <= 1000
        to_id = from_id - count
    except:
        raise e.ArgumentError(src.lang)

    delete = list(range(from_id, to_id, -1))
    for l in range(0, count, 100):
        d = delete[l:l+100]
        await client.delete_messages(msg.chat.id, d)

    msg = await msg.answer(src.text.chat.admin.purge.format(count=len(delete)), reply_markup=system.delete_this.inline)
