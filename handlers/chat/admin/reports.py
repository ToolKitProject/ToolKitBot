import typing as p

from aiogram import types as t

from libs import filters as f, utils as u
from libs.classes.CommandParser import ParsedArgs
from libs.src import any
from libs.objects import Database
from libs.classes.Database import LogType as l


@any.parsers.report(
    f.user.is_admin,
    f.message.is_chat,
    u.write_action,
    u.get_help
)
async def report(msg: t.Message, parsed: ParsedArgs):
    for user in parsed.targets:
        Database.add_log(msg.chat.id, msg.from_user.id, user.id, l.REPORT, msg.date)
