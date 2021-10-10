from aiogram import types as t

from handlers.chat.admin.restrict import process_restrict, command_text
from libs.chat import Chat
from libs.command_parser import ParsedArgs
from libs.database import LogType as l
from libs.user import User
from locales import other, text
from src import filters as f
from src import utils as u
from src.instances import Database


@other.parsers.report(
    f.user.is_admin,
    f.message.is_chat,
    u.write_action,
    u.get_help
)
async def report(msg: t.Message, parsed: ParsedArgs):
    chat = await Chat.create(msg.chat)
    parsed.targets: list[User]
    executor = await User.create(msg.from_user)

    txt = text.chat.admin.report.format(
        reason=parsed.reason,
        admin=executor.ping,
    )
    restrict = []

    await u.raise_permissions_errors(parsed.targets, await msg.chat.get_administrators())
    for user in parsed.targets:
        Database.add_log(chat.id, msg.from_user.id, user.id, l.REPORT, msg.date)
        reports = user.get_reports(chat)

        if reports >= chat.report_count:
            restrict.append(user)

        txt += text.chat.admin.report_sample.format(
            user=user.ping,
            user_reports=reports,
            max_reports=chat.report_count
        )

    if parsed.targets:
        await msg.answer(txt)

    if restrict:
        parsed_restrict = await other.parsers.restrict.parse(chat.report_command, check=False)
        parsed_restrict.targets = restrict
        parsed_restrict.reason = text.chat.admin.report_reason

        await process_restrict(parsed_restrict)
        txt, *_ = command_text(parsed_restrict, executor)
        await msg.answer(txt)
