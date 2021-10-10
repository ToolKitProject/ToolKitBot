import typing as p
from datetime import datetime

from aiogram import types as t

from bot import dp
from libs.chat import Chat
from libs.command_parser import ParsedArgs
from libs.errors import MyError, ERRORS, IGNORE, ForceError
from libs.user import User
from locales import other
from src.instances import Database


@dp.errors_handler()
async def errors(_, error: p.Union[MyError, Exception]):
    """
    Errors handler
    """
    if error.__class__ in ERRORS:  # If my errors
        await error.answer()
    elif error.__class__ in IGNORE:  # If errors must be ignored
        return True
    else:  # Other errors
        my_err = ForceError(f"⚠ {error.__class__.__name__}:{error.args[0]}", 0, True, False)
        await my_err.log()
        await my_err.answer()

    return True


@other.parsers.test()
async def test_xd(msg: t.Message, parsed: ParsedArgs):
    a = t.InlineKeyboardMarkup().add(
        t.InlineKeyboardButton("any text", callback_data="z" * 64)
    )

    await msg.answer("any text", reply_markup=a)
