import typing as p
from copy import copy
from datetime import timedelta, datetime

from aiogram import types as t

from bot import bot
from handlers.chat.admin import purge
from libs import filters as f, utils as u
from libs.classes.CommandParser import ParsedArgs, dates
from libs.classes.User import User
from libs.objects import MessageData, Database
from libs.src import any, text, buttons


@any.parsers.restrict(
    f.message.is_chat,
    f.bot.has_permission("can_restrict_members"),
    f.user.has_permission("can_restrict_members"),
    u.write_action,
    u.get_help
)
async def command(msg: t.Message, parsed: ParsedArgs):
    """
    Restrict command handler
    """

    executor = await User.create(msg.from_user)  # Get executor of command
    # If poll
    if parsed.flags.poll:
        txt, rm = await get_poll_text(parsed)
        msg = await msg.answer_poll(
            txt,
            text.chat.admin.options_poll,

            is_anonymous=False,
            reply_markup=rm,
        )
    else:
        # Execute restrict command
        if await execute_action(parsed, msg.chat.id):
            txt, rm = await get_text(parsed, executor)  # Get text
            msg = await msg.answer(txt, reply_markup=rm)  # Send text

    with MessageData.data(msg) as data:
        data.parsed = parsed  # Save message data


@buttons.chat.admin.undo(f.message.is_chat, f.user.has_permission("can_restrict_members"))
async def undo(clb: t.CallbackQuery):
    executor = await User.create(clb.from_user)  # Get executor of command
    with MessageData.data() as data:
        parsed: ParsedArgs = data.parsed  # Get parsed obj
        await execute_action(parsed, clb.message.chat.id, True)  # Execute *undo* command
        txt, rm = await get_text(parsed, executor)  # Get text
        await clb.message.edit_text(txt, reply_markup=rm)  # Edit message text
        data.parsed = parsed  # Save parsed obj


async def execute_action(parsed: ParsedArgs, chat_id: str, undo: bool = False):
    type: str = parsed.command.text
    users: p.List[User] = parsed.targets
    until: timedelta = parsed.until

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

            if parsed.flags.clear_history and type in ["ban", "mute", "kick"]:
                to_date = datetime.now()
                from_date = to_date - timedelta(hours=1)
                msg_ids = Database.get_messages_id(user.id, chat_id, from_date, to_date)
                await purge.execute(msg_ids, chat_id)

            result = True
        except Exception as error:
            txt = f"⚠ {user.link}\n" \
                  f"┗━{error.args[0]}"
            await bot.send_message(chat_id, txt)
            parsed.targets.remove(user)
    return result


async def get_poll_text(parsed: ParsedArgs):
    type: str = parsed.command.text
    adm = text.chat.admin

    txt = None
    rm = buttons.chat.admin.poll

    if type == "ban":
        txt = adm.ban_poll
    elif type == "unban":
        txt = adm.unban_poll
    elif type == "kick":
        txt = adm.kick_poll
    elif type == "mute":
        txt = adm.mute_poll
    elif type == "unmute":
        txt = adm.unmute_poll

    users = " ".join([u.full_name for u in parsed.targets])
    txt = txt.format(user=users)

    return txt, rm


async def get_text(parsed: ParsedArgs, executor: User) -> p.Tuple[str, t.InlineKeyboardMarkup]:
    adm = text.chat.admin

    type: str = parsed.command.text.lower()
    users: p.List[User] = parsed.targets
    multi = len(users) > 1

    txt = None
    rm = buttons.chat.admin.undo.menu

    if type == "ban":
        txt = adm.multi_ban if multi else adm.ban
    elif type == "unban":
        txt = adm.multi_unban if multi else adm.unban
    elif type == "kick":
        txt = adm.multi_kick if multi else adm.kick
        rm = None
    elif type == "mute":
        txt = adm.multi_mute if multi else adm.mute
    elif type == "unmute":
        txt = adm.multi_unmute if multi else adm.unmute

    users = " ".join([u.link for u in users])

    until = adm.forever
    if parsed.until:
        if dates.forever(parsed.until):
            until: str = adm.forever
        else:
            until: str = (dates.now() + parsed.until).strftime("%Y %m %d")

    txt = txt.format(
        user=users,
        reason=parsed.reason,
        admin=executor.link,
        until=until
    )

    if parsed.flags.clear_history and type in ["ban", "mute", "kick"]:
        txt += text.chat.admin.clear_history

    return txt, rm
