from datetime import datetime
from typing import List, Text, Tuple, Union

from aiogram.types import *
from aiogram.types.inline_keyboard import InlineKeyboardMarkup as IM
from pyrogram.methods import users
from bot import bot, dp
from libs.classes import Admin, AdminCommandParser, User, get_help
from libs.classes.Errors import *
from libs.classes.Localisation import UserText
from libs.objects import MessageData


def is_chat(msg: Union[CallbackQuery, Message]):
    if type(msg) == CallbackQuery:
        msg = msg.message
    return msg.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]


@dp.message_handler(is_chat, commands=["ban", "unban", "kick", "mute", "unmute"])
async def command(msg: Message):
    """
    Обрабочик команды
    """
    await msg.answer_chat_action(ChatActions.TYPING)
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
async def undo(clb: CallbackQuery):
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
            await user.ban(until)
        elif action == "unban":
            await user.unban()
        elif action == "kick":
            await user.kick()
        elif action == "mute":
            await user.mute(until)
        elif action == "unmute":
            await user.unmute()


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
