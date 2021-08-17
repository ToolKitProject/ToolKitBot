import typing as p

from aiogram import types as t

from libs import filters as f
from libs.classes import Utils as u
from libs.classes.User import User
from libs.src import any


@any.parsers.report(
    f.message.is_chat,
    u.write_action,
    u.get_help
)
async def report(msg: t.Message):
    parsed = await any.parsers.report.parse(msg)
    users: p.List[User] = parsed.user

    text = ""
    for user in users:
        user.reports[msg.chat.id] += 1
        text += f"{user.link} - {user.global_reports}"

    await msg.reply(text)
