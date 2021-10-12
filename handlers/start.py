from __future__ import annotations

from aiogram import types as t

from bot import dp
from libs.command_parser import ParsedArgs
from libs.errors import MyError, ERRORS, IGNORE, ForceError
from locales import other
from src.instances import Cache


@dp.errors_handler()
async def errors(_, error: MyError | Exception):
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
    Cache.expire()
    await msg.answer("All cache expired")
