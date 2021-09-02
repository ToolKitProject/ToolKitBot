import typing as p
from datetime import datetime, timedelta

from bot import dp
from aiogram import types as t

from libs.classes.Chat import Chat
from libs.classes.Errors import MyError, ERRORS, IGNORE, ForceError
from libs.classes.User import User
from libs.objects import Database
from libs.src import any, text
from libs.classes.CommandParser import ParsedArgs


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


@any.parsers.test()
async def test_xd(msg: t.Message, parsed: ParsedArgs):
    td = datetime.now()
    fd = td - parsed.delta
    logs = Database.get_logs_by_date(fd, td)
    txt = "id - Чат Исполнитель Цель Тип Время\n"
    for log in logs:
        chat = await Chat.create(log.chat_id)
        target = await User.create(log.target_id)
        executor = await User.create(log.executor_id)

        txt += f"{log.log_id} - {chat.link} {executor.link} {target.link} {log.type} {log.date.isoformat(' ')}\n"
    await msg.answer(txt)
