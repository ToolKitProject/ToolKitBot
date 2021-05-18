from typing import *

from aiogram import types as t
from aiogram.types import InlineKeyboardMarkup as IM
from bot import dp
from libs.classes import AdminCommandParser
from libs.classes import Errors as e
from libs.classes import User
from libs.classes.Utils import (alias, bot_has_permission, get_help,
                                has_permission, is_chat, is_reply, mark_write)
from libs.objects import MessageData
from libs.src import buttons, system


@dp.message_handler(is_chat, is_reply, alias, bot_has_permission("can_restrict_members"), has_permission("can_restrict_members"), content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_command(msg: t.Message):
    await mark_write(msg)

    target: User = await User(msg.reply_to_message.from_user, chat=msg.chat)

    command = await alias(msg, False)
    parser: AdminCommandParser = await AdminCommandParser(msg, command, target=target)
    await execute_action(parser)

    text, rm = await get_text(parser)
    message = await msg.reply(text, reply_markup=rm)
    with await MessageData(message) as data:
        data.parser = parser


@dp.message_handler(is_chat, get_help, bot_has_permission("can_restrict_members"), has_permission("can_restrict_members"),  commands=system.restrict_commands)
async def command(msg: t.Message):
    """
    Обрабочик команды
    """
    await mark_write(msg)

    target = None
    if await is_reply.check(msg):
        target: User = await User(msg.reply_to_message.from_user, chat=msg.chat)

    parser: AdminCommandParser = await AdminCommandParser(msg, target=target)
    text, rm = await get_text(parser)

    await execute_action(parser)
    message = await msg.reply(text, reply_markup=rm)
    with await MessageData(message) as data:
        data.parser = parser


@buttons.chat.admin.undo.set_action(is_chat, has_permission("can_delete_messages"))
async def undo(clb: t.CallbackQuery):
    """
    Обрабочик кнопки undo
    """
    msg = clb.message
    with await MessageData(msg) as data:
        parser: AdminCommandParser = data.parser
        parser.action = await parser.undo()
        parser.owner = await User(clb.from_user, chat=clb.message.chat)
        await parser.re_parse_date()

    await execute_action(parser)
    text, rm = await get_text(parser)

    await msg.edit_text(text, reply_markup=rm)


async def execute_action(parser: AdminCommandParser):
    act = parser.action

    if parser.revoke_admin and not await parser.owner.has_permission("can_promote_members"):
        raise e.HasNotPermission(parser.owner.lang)
    if parser.delete_all_messages and not await parser.owner.has_permission("can_delete_messages"):
        raise e.HasNotPermission(parser.owner.lang)

    for user in parser.targets:
        if act == "ban":
            await user.ban(parser.until, parser.delete_all_messages, parser.revoke_admin)
        elif act == "unban":
            await user.unban()
        elif act == "kick":
            await user.kick(parser.delete_all_messages, parser.revoke_admin)
        elif act == "mute":
            await user.mute(parser.until, parser.revoke_admin)
        elif act == "unmute":
            await user.unmute()


async def get_text(parser: AdminCommandParser) -> Tuple[str, IM]:
    action = parser.action
    src = parser.owner.src

    if len(parser.targets) > 1:
        action = "multi_" + action

    text: str = getattr(src.text.chat.admin, action)
    rm = src.buttons.chat.admin.undo
    if parser.action in ["kick"]:
        rm = None

    text = text.format(
        users=parser.format_users,
        reason=parser.reason,
        admin=parser.owner.ping,
        until=parser.format_until
    )

    return text, rm.inline if rm else None
