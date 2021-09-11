import typing as p

from aiogram import types as t

from libs.chat import Chat
from libs.command_parser import ParsedArgs
from libs.database import LogType as l
from libs.user import User
from src.instances import Database
from src import filters as f, utils as u
from locales import other, text


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
        Database.add_log(chat.id, msg.from_user.id, user.id, l.REPORT, msg.date)
        
        txt += text.chat.admin.report_sample.format(
            user=user.ping,
            user_reports=user.get_reports(chat),
            max_reports=chat.max_reports
        )

    await msg.answer(txt)
