import asyncio

from libs.classes.Utils import promote_admin, removed_member, restrict_admin

from libs.classes.Utils import add_member, chek
import logging
import traceback
from typing import List

from aiogram import types as t
from bot import dp, bot
from libs.classes import Menu, Chat
from libs.classes.Errors import *
from libs.objects import MessageData, Database
from libs.src import system


@system.back.set_action()
async def back(clb: t.CallbackQuery):
    msg = clb.message
    with await MessageData(msg) as data:
        history: List[Menu] = data.history
        try:
            history.pop(-1)
            await history[-1].edit(msg, False)
            data.history = history
        except Exception as e:
            pass


@dp.my_chat_member_handler(add_member)
async def bot_join(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(chat=upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.start_text)


@dp.my_chat_member_handler(removed_member)
async def removed_member(upd: t.ChatMemberUpdated):
    Database.delete_chat(upd.chat.id)


@dp.my_chat_member_handler(promote_admin)
async def bot_promote(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(chat=upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.promote_admin)


@dp.my_chat_member_handler(restrict_admin)
async def bot_restrict(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(chat=upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.restrict_admin)


@dp.message_handler(chek, content_types=[t.ContentType.TEXT, t.ContentType.PHOTO])
async def chek(msg: t.Message):
    pass


@dp.errors_handler()
async def errors(update: t.Update, error: Exception):
    """
    Обрабочик ошибок
    """

    async def delete(*msgs: t.Message, sleep: int = 2):
        await asyncio.sleep(sleep)
        for msg in msgs:
            try:
                await msg.delete()
            except:
                pass

    if update.message:
        msg = update.message
        answer = msg.answer
    elif update.callback_query:
        msg = update.callback_query.message
        answer = update.callback_query.answer
    else:
        return

    errorText: str
    if error.__class__ in ERRORS:
        errorText = error.args[0]
        m = await answer(errorText)
        try:
            del_time = error.args[1]
            await delete(m)
        except:
            pass
    elif error.__class__ in IGNORE:
        pass
        # logging.info(f"Error skipped {error.__class__.__name__}")
    else:
        txt = f"{traceback.format_exc()}" + \
            f"User: {msg.from_user.mention}\n" + \
            f"Message: {msg.text} \n"
        logging.error(txt)
        await answer(f"⚠ {error.__class__.__name__}: {error.args[0]}")
        # for id in config.owners:
        #     await bot.send_message(id, txt)

    return True
