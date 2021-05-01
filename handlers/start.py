import asyncio
import logging
import traceback
from typing import List

from aiogram import types as t
from bot import dp, bot
from libs.classes import chek, Menu
from libs.classes.Errors import *
from libs.objects import MessageData
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


@dp.message_handler(chek, content_types=[t.ContentType.ANY])
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
