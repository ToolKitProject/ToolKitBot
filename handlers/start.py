import typing as p

from aiogram import types as t

from bot import dp
from libs import filters as f
from libs.classes.Buttons import Button
from libs.classes.Chat import Chat
from libs.classes.Errors import MyError, ERRORS, IGNORE, ForceError
from libs.classes.Settings import Settings, Property, Elements
from libs.classes.User import User
from libs.objects import Database, MessageData

chek_types = t.ContentType.all()
chek_types.remove(t.ContentType.LEFT_CHAT_MEMBER)


async def check(msg: t.Message):
    """
    Creates records in the database
    """

    if msg.content_type not in chek_types:
        return False

    if await f.message.is_chat.check(msg):
        chat = await Chat.create()
    user = await User.create()

    if await f.message.is_chat.check(msg):
        mode = chat.statistic_mode
        if user.statistic_mode < mode:
            mode = user.statistic_mode

        if mode == 2:
            Database.add_message(msg.from_user.id, msg.chat.id, msg.text, msg.content_type, msg.date)
        elif mode == 1:
            Database.add_message(msg.from_user.id, msg.chat.id, None, msg.content_type, msg.date)

    return False


# @any.command.AdminCommandParser()
# @dp.edited_message_handler(commands=["test"])
# @dp.callback_query_handler(test_clb)
# @dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):  # Test func
    settings = Settings("Настройки").add(
        Property("Текста", "Настроить текста", "texts", row_width=1).add(
            Button("Просто кнопка", "btn"),
            Elements("{key} → {value}", "elem")
        )
    )
    s = {
        "texts": {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            "key4": "value4",
            "key5": "value5",
            "key6": "value6",
        }
    }

    menu = settings.menu(s)
    await msg.answer(s, "None")
    await menu.send()


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


@dp.message_handler(check, content_types=t.ContentType.ANY)
async def check():
    """
    Execute check func
    """
    pass
