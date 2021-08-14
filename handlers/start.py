import typing as p

from aiogram import types as t

from bot import dp
from libs import filters as f
from libs.classes.Buttons import Menu, Button, Submenu
from libs.classes.Chat import Chat
from libs.classes.Errors import MyError, ERRORS, IGNORE, ForceError
from libs.classes.Settings import Settings, Property, Elements
from libs.objects import Database, MessageData


async def test_clb(clb: t.CallbackQuery):
    with await MessageData.data(clb.message) as data:
        text = f"{clb.data}\n"
        for k, v in data.storage.items():
            text += f"{k} - {v} \n"
        print(text)

    return False


async def check(msg: t.Message):
    """
    Creates records in the database
    """
    if await f.message.is_chat.check(msg) and not Database.get_chat(msg.chat.id):
        await Chat.create()
    Database.get_user(msg.from_user.id)

    if msg.chat.type != t.ChatType.PRIVATE:
        Database.add_message(msg)

    return False


# @any.command.AdminCommandParser()
# @dp.edited_message_handler(commands=["test"])
# @dp.callback_query_handler(test_clb)
@dp.message_handler(commands=["test"])
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
