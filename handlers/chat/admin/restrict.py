import typing as p
from copy import copy
from datetime import timedelta

from aiogram import types as t

from bot import dp, bot
from libs.classes.CommandParser import _ParsedArgs, dates
from libs.classes.User import User
from libs.classes.Utils import (alias, bot_has_permission as bhp, get_help,
                                has_permission as hp, is_chat, is_reply)
from libs.objects import MessageData
from libs.src import any
from libs.src import buttons


@any.command.AdminCommandParser(is_chat, bhp("can_restrict_members"), hp("can_restrict_members"), get_help)
async def command(msg: t.Message):
    executor = await User.create(msg.from_user)
    src = executor.src
    parsed = await src.any.command.AdminCommandParser.parse(msg)
    if await execute_action(parsed, msg.chat.id):
        text, rm = await get_text(parsed, executor)
        msg = await msg.answer(text, reply_markup=rm)
        with await MessageData.data(msg) as data:
            data.parsed = parsed


@buttons.chat.admin.undo(is_chat, hp("can_restrict_members"))
async def undo(clb: t.CallbackQuery):
    executor = await User.create(clb.from_user)
    with await MessageData.data(clb.message) as data:
        parsed: _ParsedArgs = data.parsed
        await execute_action(parsed, clb.message.chat.id, True)
        text, rm = await get_text(parsed, executor)
        await clb.message.edit_text(text, reply_markup=rm)
        data.parsed = parsed


async def execute_action(parsed: _ParsedArgs, chat_id: str, undo: bool = False):
    type: str = parsed.command.text
    users: p.List[User] = parsed.user
    until: timedelta = parsed.date if parsed.date else None

    result = False

    if undo:
        if type.startswith("un"):
            type = type.removeprefix("un")
        else:
            type = f"un{type}"
        parsed.command.text = type

    for user in copy(users):
        try:
            if type == "ban":
                await user.ban(chat_id, until)
            elif type == "unban":
                await user.unban(chat_id)
            elif type == "kick":
                await user.kick(chat_id)
            elif type == "mute":
                await user.mute(chat_id, until)
            elif type == "unmute":
                await user.unmute(chat_id)
            result = True
        except Exception as error:
            text = f"⚠ {user.link}\n" \
                   f"┗━{error.args[0]}"
            await bot.send_message(chat_id, text)
            parsed.user.remove(user)
    return result


async def get_text(parsed: _ParsedArgs, executor: User) -> p.Tuple[str, t.InlineKeyboardMarkup]:
    src = executor.src
    adm = src.text.chat.admin

    type: str = parsed.command.text
    users: p.List[User] = parsed.user
    multi = len(users) > 1

    text = None
    rm = src.buttons.chat.admin.undo.inline

    if type == "ban":
        text = adm.multi_ban if multi else adm.ban
    elif type == "unban":
        text = adm.multi_unban if multi else adm.unban
    elif type == "kick":
        text = adm.multi_kick if multi else adm.kick
        rm = None
    elif type == "mute":
        text = adm.multi_mute if multi else adm.mute
    elif type == "unmute":
        text = adm.multi_unmute if multi else adm.unmute

    users = " ".join([u.link for u in users])
    reason: str = parsed.reason.raw if parsed.reason else adm.reason_empty

    until = adm.forever
    if parsed.date:
        if dates.forever(parsed.date):
            until: str = adm.forever
        else:
            until: str = (dates.now() + parsed.date).strftime("%Y %m %d")

    text = text.format(
        user=users,
        reason=reason,
        admin=executor.link,
        until=until
    )

    return text, rm
