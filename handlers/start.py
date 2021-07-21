import typing as p

from aiogram import types as t

from bot import dp
from libs import filters as f
from libs.classes.Chat import Chat
from libs.classes.Errors import MyError, ERRORS, IGNORE, ForceError
from libs.objects import Database


async def check(msg: t.Message):
    """
    Creates records in the database
    """
    if await f.message.is_chat.check(msg) and not Database.get_chat(msg.chat.id):
        await Chat.create()
    if not Database.get_user(msg.from_user.id):
        Database.add_user(msg.from_user.id)

    return False


# @dp.callback_query_handler(test_clb)
# @any.command.AdminCommandParser()
# @dp.edited_message_handler(commands=["test"])
@dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):  # Test func
    pass


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


@dp.message_handler(check, content_types=[t.ContentType.TEXT, t.ContentType.PHOTO])
async def check():
    """
    Execute check func
    """
    pass
