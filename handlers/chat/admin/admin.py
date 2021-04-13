from libs.objects import MessageData
from libs.classes.Errors import *
from aiogram import types
from bot import dp, client
from libs.classes import CommandParser, User, UserText, get_help
from libs.classes import CommandParser


def is_chat(msg: types.Message):
    """
    Проверка на тип чата
    """
    return msg.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]


@dp.message_handler(lambda msg: is_chat(msg), commands=["ban", "unban", "kick", "mute", "unmute"])
async def command(msg: types.Message):
    """
    Обрабочик команды
    """
    await msg.answer_chat_action(types.ChatActions.TYPING)
    member = await msg.chat.get_member(msg.from_user.id)
    if not (member.can_restrict_members or member.is_chat_creator()):  # Проверка прав
        raise HasNotPermission(msg.from_user.language_code)
    if msg.text == msg.get_command():  # Вывод помощи
        await get_help(msg)
        return

    parser: CommandParser = await CommandParser(msg)
    # Получаем текст и кнопку действия
    text, rm = await get_text(parser, msg.from_user)
    await action(parser, msg)  # Выполняем действие команды
    msg = await msg.reply(text, reply_markup=rm)
    with await MessageData(msg) as data:
        data.parser = parser


@dp.callback_query_handler(lambda clb: clb.data == "undo")
async def undo(clb: types.CallbackQuery):
    """
    Обрабочик кнопки undo
    """
    msg = clb.message

    with await MessageData(msg) as data:
        parser: CommandParser = data.parser
        parser.action = parser.undo_action
        parser.type = parser.undo_type
        await parser.to_undo()
        data.parser = parser

    await action(parser, msg)
    text, rm = await get_text(parser, clb.from_user)
    await msg.edit_text(text, reply_markup=rm)


async def get_text(parser: CommandParser, usr: types.User):
    """
    Возвращает локализованные текст и кнопу
    """
    user = User(await client.get_chat(usr.id))
    src = UserText(usr.language_code)
    text = getattr(src.text.chat.admin, parser.type)

    text = text.format(
        users=parser.format_users,
        reason=parser.reason,
        adminuser=user.link,
        until=parser.format_until
    )

    rm = src.buttons.chat.admin.undo
    if parser.action in ["kick"]:
        rm = None
    return text, rm


async def action(parser: CommandParser, msg: types.Message):
    """
    Выполняет действие
    """
    for user in parser.users:
        try:
            action: user.ban = getattr(user, parser.action)
            await action(msg.chat.id, parser)
        except:
            pass
