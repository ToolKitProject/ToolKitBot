from libs.classes.Errors import *
from aiogram import types
from bot import dp, client
from libs.classes import CommandParser, User, UserText, get_help


def is_chat(msg: types.Message):
    return msg.chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]


@dp.message_handler(lambda msg: is_chat(msg), commands=["ban", "unban", "kick", "mute", "unmute"])
async def command(msg: types.Message):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    member = await msg.chat.get_member(msg.from_user.id)
    if not (member.can_restrict_members or member.is_chat_creator()):  # Проверка прав
        raise HasNotPermission(msg.from_user.language_code)
    if msg.text == msg.get_command():  # Вывод помощи
        await get_help(msg)
        return

    parser: CommandParser = await CommandParser(msg)
    text = await get_text(parser, msg)
    await action(parser, msg)
    await msg.reply(text)


async def get_text(parser: CommandParser, msg: types.Message):
    user = User(await client.get_chat(msg.from_user.id))
    src = UserText(msg.from_user.language_code)
    text = getattr(src.text.chat.admin, parser.type)

    text = text.format(
        users=parser.format_users,
        reason=parser.reason,
        adminuser=user.link,
        until=parser.format_until
    )

    return text


async def action(parser: CommandParser, msg: types.Message):
    for user in parser.users:
        try:
            action: user.ban = getattr(user, parser.action)
            await action(msg.chat.id, parser)
        except:
            pass
