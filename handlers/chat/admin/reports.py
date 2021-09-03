import typing as p

from aiogram import types as t

from libs.chat import Chat
from libs.commandParser import ParsedArgs
from libs.database import LogType as l
from libs.user import User
from src.objects import Database
from src import text, filters as f, utils as u
from src import other


@other.parsers.report(
    f.user.is_admin,
    f.message.is_chat,
    u.write_action,
    u.get_help
)
async def report(msg: t.Message, parsed: ParsedArgs):
    chat = await Chat.create(msg.chat)
    executor = await User.create(msg.from_user)
    users: p.List[User] = parsed.targets

    txt = text.chat.admin.report.format(
        reason=parsed.reason,
        admin=executor.ping,
    )

    for user in users:
        txt += text.chat.admin.report_sample.format(
            user=user.ping,
            user_reports=user.get_reports(chat),
            max_reports=chat.max_reports
        )

        Database.add_log(chat.id, msg.from_user.id, user.id, l.REPORT, msg.date)

    await msg.answer(txt)
