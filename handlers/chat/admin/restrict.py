import typing as p
from copy import copy
from datetime import timedelta

from aiogram import types as t

from bot import bot
from libs import filters as f
from libs.classes.CommandParser import ParsedArgs, dates
from libs.classes.Localisation import UserText
from libs.classes.User import User
from libs.classes import Utils as u
from libs.objects import MessageData
from libs.src import any
from libs.src import buttons


@any.parsers.restrict(
    f.message.is_chat,
    f.bot.has_permission("can_restrict_members"),
    f.user.has_permission("can_restrict_members"),
    u.write_action,
    u.get_help
)
async def command(msg: t.Message):
    """
    Restrict command handler
    """

    executor = await User.create()  # Get executor of command
    src = executor.src
    parsed = await src.any.parsers.restrict.parse(msg)  # Parse command

    # If poll
    if parsed.flags.poll:
        text, rm = await get_poll_text(parsed, executor)
        msg = await bot.send_poll(
            msg.chat.id,

            text,
            src.text.chat.admin.options_poll,

            is_anonymous=False,
            reply_markup=rm,
        )
    else:
        # Execute restrict command
        if await execute_action(parsed, msg.chat.id):
            text, rm = await get_text(parsed, executor)  # Get text
            msg = await msg.answer(text, reply_markup=rm)  # Send text

    with await MessageData.data(msg) as data:
        data.parsed = parsed  # Save message data


@buttons.chat.admin.undo(f.message.is_chat, f.user.has_permission("can_restrict_members"))
async def undo(clb: t.CallbackQuery):
    executor = await User.create()  # Get executor of command
    with await MessageData.data(clb.message) as data:
        parsed: ParsedArgs = data.parsed  # Get parsed obj
        await execute_action(parsed, clb.message.chat.id, True)  # Execute *undo* command
        text, rm = await get_text(parsed, executor)  # Get text
        await clb.message.edit_text(text, reply_markup=rm)  # Edit message text
        data.parsed = parsed  # Save parsed obj


async def execute_action(parsed: ParsedArgs, chat_id: str, undo: bool = False):
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


async def get_poll_text(parsed: ParsedArgs, executor: User):
    src = executor.src
    type: str = parsed.command.text
    adm = src.text.chat.admin

    text = None
    rm = src.buttons.chat.admin.poll

    if type == "ban":
        text = adm.ban_poll
    elif type == "unban":
        text = adm.unban_poll
    elif type == "kick":
        text = adm.kick_poll
    elif type == "mute":
        text = adm.mute_poll
    elif type == "unmute":
        text = adm.unmute_poll

    users = " ".join([u.full_name for u in parsed.user])
    text = text.format(user=users)

    return text, rm


async def get_text(parsed: ParsedArgs, executor: User) -> p.Tuple[str, t.InlineKeyboardMarkup]:
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
