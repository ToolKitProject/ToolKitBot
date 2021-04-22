from aiogram.types import *
from typing import *
from bot import dp, bot


def is_chat(msg: Union[CallbackQuery, Message]):
    if type(msg) == CallbackQuery:
        msg = msg.message
    return msg.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]


@dp.chat_member_handler()
async def member_update(mbr: ChatMemberUpdated):
    await bot.send_message(mbr.chat.id, f"Пользователь {mbr.new_chat_member.user.mention} обновился")
