from typing import *

from aiogram import types as t
from aiogram.types import InlineKeyboardMarkup as IM
from bot import dp
from libs.classes import AdminCommandParser, User, UserText, get_help, is_chat
from libs.classes.Errors import *
from libs.objects import MessageData


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


@dp.callback_query_handler(lambda clb: clb.data == "undo")
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
    src = UserText(parser.owner.lang)

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

    return text, rm
