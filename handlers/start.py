import asyncio
import logging
import traceback
from typing import List

from aiogram import types as t
from bot import bot, dp
from libs.classes import Chat, Menu, ChatSettings, UserText
from libs.classes.Errors import *
from libs.classes.Utils import (add_member, chek, is_chat, is_private,
                                promote_admin, removed_member, restrict_admin)
from libs.objects import Database, MessageData
from libs.src import system


async def test_clb(clb: t.CallbackQuery):
    await clb.answer(clb.data)


# @dp.callback_query_handler(test_clb)
# @dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):
    test = ChatSettings.get(-1001197098429, msg.from_user.language_code)
    await test.send(msg)


@dp.message_handler(is_private, commands=["start"])
async def start(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    await msg.answer(src.text.private.start_text)


@system.delete_this.set_action(is_chat)
async def delete_this(clb: t.CallbackQuery):
    await clb.message.delete()


@system.back.set_action()
async def back(clb: t.CallbackQuery):
    msg = clb.message
    with await MessageData(msg) as data:
        try:
            history: List[Menu] = data.history
            history.pop(-1)
            await history[-1].edit(msg, False)
            data.history = history
        except Exception as e:
            raise BackError(clb.from_user.language_code)


@dp.my_chat_member_handler(add_member)
async def bot_join(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.start_text)


@dp.my_chat_member_handler(removed_member)
async def removed_member(upd: t.ChatMemberUpdated):
    Database.delete_chat(upd.chat.id)


@dp.my_chat_member_handler(promote_admin)
async def bot_promote(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.promote_admin)


@dp.my_chat_member_handler(restrict_admin)
async def bot_restrict(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(upd.chat)
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
        if answer == msg.answer:
            m = await answer(errorText, reply_markup=system.delete_this.inline)
        else:
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
        logTXT = f"⚠ {error.__class__.__name__}: {error.args[0]}"
        if answer == msg.answer:
            await answer(logTXT, reply_markup=system.delete_this.inline)
        else:
            await answer(logTXT)

        # for id in config.owners:
        #     await bot.send_message(id, txt)

    return True
