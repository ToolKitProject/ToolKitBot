from datetime import timedelta

from aiogram import types as t

from handlers.chat.admin.purge import process_purge
from libs.command_parser import ParsedArgs
from libs.user import User
from locales import other, text, buttons
from src import filters as f
from src import utils as u
from src.instances import MessageData, Database
from src.parsers import dates


@other.parsers.restrict(
    f.message.is_chat,
    f.bot.has_permission("can_restrict_members"),
    f.user.has_permission("can_restrict_members"),
    u.write_action,
    u.get_help
)
async def restrict_command(msg: t.Message, parsed: ParsedArgs):
    await u.raise_permissions_errors(parsed.targets, await msg.chat.get_administrators())
    if parsed.targets:
        executor = await User.create(msg.from_user)

        if parsed.flags.poll or parsed.flags.anonym:
            txt, rm = poll_text(parsed)
            msg = await msg.answer_poll(
                txt,
                text.chat.admin.options_poll,
                reply_markup=rm,

                is_anonymous=parsed.flags.anonym,
                open_period=parsed.flags.poll_delta.value.total_seconds()
            )
        else:
            await process_restrict(parsed)
            txt, rm = command_text(parsed, executor)
            msg = await msg.answer(txt, reply_markup=rm)

        with MessageData.data(msg) as data:
            data.parsed = parsed


@buttons.chat.admin.undo(
    f.message.is_chat,
    f.user.has_permission("can_restrict_members")
)
async def undo_restrict(clb: t.CallbackQuery):
    executor = await User.create(clb.from_user)
    parsed: ParsedArgs = MessageData.data().parsed

    if parsed.command.text.startswith("un"):
        parsed.command.text = parsed.command.text.removeprefix("un")
    else:
        parsed.command.text = f"un{parsed.command.text}"

    await process_restrict(parsed)
    txt, rm = command_text(parsed, executor)
    await clb.message.edit_text(txt)
    await MessageData.delete(clb.message)


def poll_text(parsed: ParsedArgs):
    type = parsed.command.text
    f_users = " ".join([u.full_name for u in parsed.targets])
    result = ""

    if type == "ban":
        result = text.chat.admin.ban_poll
    elif type == "unban":
        result = text.chat.admin.unban_poll
    elif type == "kick":
        result = text.chat.admin.kick_poll
    elif type == "mute":
        result = text.chat.admin.mute_poll
    elif type == "unmute":
        result = text.chat.admin.unmute_poll

    result = result.format(user=f_users)

    return result, buttons.chat.admin.poll


def command_text(parsed: ParsedArgs, executor: User):
    type = parsed.command.text
    users = " ".join([u.ping for u in parsed.targets])
    result = ""

    if len(parsed.targets) > 1:
        if type == "ban":
            result = text.chat.admin.multi_ban
        elif type == "unban":
            result = text.chat.admin.multi_unban
        elif type == "kick":
            result = text.chat.admin.multi_kick
        elif type == "mute":
            result = text.chat.admin.multi_mute
        elif type == "unmute":
            result = text.chat.admin.multi_unmute
    else:
        if type == "ban":
            result = text.chat.admin.ban
        elif type == "unban":
            result = text.chat.admin.unban
        elif type == "kick":
            result = text.chat.admin.kick
        elif type == "mute":
            result = text.chat.admin.mute
        elif type == "unmute":
            result = text.chat.admin.unmute

    if dates.forever(parsed.until):
        until = text.chat.admin.forever
    else:
        until = (dates.now() + parsed.until).strftime("%Y %m %d")

    result = result.format(
        user=users,
        reason=parsed.reason,
        admin=executor.ping,
        until=until
    )

    if parsed.flags.clear_history and type in ["ban", "mute", "kick"]:
        result += text.chat.admin.clear_history

    if type == "kick":
        return result, None
    else:
        return result, buttons.chat.admin.undo.menu


async def process_restrict(parsed: ParsedArgs):
    parsed.targets: list[User]
    chat_id = t.Chat.get_current().id
    type = parsed.command.text

    for user in parsed.targets:
        try:
            if type == "ban":
                await user.ban(chat_id, parsed.until)
            elif type == "unban":
                await user.unban(chat_id)
            elif type == "kick":
                await user.kick(chat_id)
            elif type == "mute":
                await user.mute(chat_id, parsed.until)
            elif type == "unmute":
                await user.unmute(chat_id)

            if parsed.flags.clear_history and type in ["ban", "mute", "kick"]:
                messages = [
                    m.message_id for m in
                    Database.get_messages(user_id=user.id, chat_id=chat_id, delta=timedelta(days=1))
                ]
                await process_purge(messages)
        except Exception:
            pass
