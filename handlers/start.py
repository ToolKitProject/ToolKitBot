import asyncio
import logging
import traceback

from aiogram import types
from bot import dp
from libs.classes.Errors import *


@dp.errors_handler()
async def errors(update: types.Update, error: Exception):
    """
    Обрабочик ошибок
    """

    async def delete(*msgs: types.Message, sleep: int = 2):
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
        await answer(errorText)
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
