from typing import *

from aiogram import types as t
from aiogram.types import InlineKeyboardMarkup as IM
from bot import dp
from libs.classes import AdminCommandParser, AdminPanel
from libs.classes import Errors as e
from libs.classes import User, UserText, alias, get_help, is_chat
from libs.classes.Errors import *
from libs.objects import MessageData
from libs.src import buttons


@dp.message_handler(is_chat, alias, content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_command(msg: t.Message):
    if not msg.reply_to_message:
        return
        # raise e.NotReply(msg.from_user.language_code)
    else:
        await msg.answer_chat_action(t.ChatActions.TYPING)
        user: AdminPanel = await AdminPanel(user=msg.reply_to_message.from_user, creator=msg.from_user)

    command = await alias(msg, False)
    parser: AdminCommandParser = await AdminCommandParser(msg, command, user=user)
    await execute_action(parser)

    text, rm = await get_text(parser)
    message = await msg.reply(text, reply_markup=rm)
    with await MessageData(message) as data:
        data.parser = parser
        data.user = msg.from_user


@dp.message_handler(is_chat, commands=["ban", "unban", "kick", "mute", "unmute"])
async def command(msg: t.Message):
    """
    Обрабочик команды
    """
    await msg.answer_chat_action(t.ChatActions.TYPING)
    if await get_help(msg):
        return

    parser: AdminCommandParser = await AdminCommandParser(msg)

    await execute_action(parser)
    text, rm = await get_text(parser)

    message = await msg.reply(text, reply_markup=rm)
    with await MessageData(message) as data:
        data.parser = parser
        data.user = msg.from_user


@buttons.chat.admin.undo.set_action(is_chat)
async def undo(clb: t.CallbackQuery):
    """
    Обрабочик кнопки undo
    """
    msg = clb.message
    with await MessageData(msg) as data:
        user: User = data.user
        if user.id != clb.from_user.id:
            raise HasNotPermission(clb.from_user.language_code)
        parser: AdminCommandParser = data.parser
        parser.action = await parser.undo()

    await execute_action(parser)
    text, rm = await get_text(parser)

    await msg.edit_text(text, reply_markup=rm)


async def execute_action(parser: AdminCommandParser):
    users = parser.users
    action = parser.action
    until = parser.until

    for user in users:
        if action == "ban":
            await user.ban(until, parser.chat)
        elif action == "unban":
            await user.unban(parser.chat)
        elif action == "kick":
            await user.kick(parser.chat)
        elif action == "mute":
            await user.mute(until, parser.chat)
        elif action == "unmute":
            await user.unmute(parser.chat)


async def get_text(parser: AdminCommandParser) -> Tuple[str, IM]:
    action = parser.action
    src = parser.owner.src

    if len(parser.users) > 1:
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
