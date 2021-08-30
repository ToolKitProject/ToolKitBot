import typing as p
from datetime import timedelta
from time import sleep, time

from aiogram import types as t
from aiogram.types import ContentType as c

from bot import dp
from libs import filters as f
from libs.classes.Chat import Chat
from libs.classes.Errors import MyError, ERRORS, IGNORE, ForceError
from libs.classes.User import User
from libs.objects import Database
from libs.objects import Cache

chek_types = [
    c.ANIMATION,
    c.AUDIO,
    c.CONTACT,
    c.DICE,
    c.DOCUMENT,
    c.GAME,
    c.LOCATION,
    c.PHOTO,
    c.POLL,
    c.STICKER,
    c.TEXT,
    c.VENUE,
    c.VIDEO,
    c.VIDEO_NOTE,
    c.VOICE
]


async def create_db_objects(msg: t.Message):
    """
    Creates records in the database
    """

    if await f.message.is_chat.check(msg):
        await Chat.create()
    await User.create()
    return True


async def add_message(msg: t.Message):
    if not (msg.content_type in chek_types and await f.message.is_chat.check(msg)):
        return True

    chat = await Chat.create()
    user = await User.create()

    mode = chat.statistic_mode
    if user.statistic_mode < mode:
        mode = user.statistic_mode

    if mode == 2:
        Database.add_message(msg.from_user.id, msg.chat.id, msg.message_id, msg.text, msg.content_type, msg.date)
    elif mode == 1:
        Database.add_message(msg.from_user.id, msg.chat.id, msg.message_id, type=msg.content_type, date=msg.date)
    elif mode == 0:
        Database.add_message(msg.from_user.id, msg.chat.id, msg.message_id)

    return True


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


@dp.message_handler(create_db_objects, add_message, lambda msg: False, content_types=t.ContentType.ANY)
async def middleware():
    """
    Execute check func
    """
    pass


@dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):  # Test func
    pass
