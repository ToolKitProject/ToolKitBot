import re
import typing as p

from aiogram import types as t

from bot import bot, dp
from libs.classes import Chat, Menu, UserText
from libs.classes import CommandParser as parser
from libs.classes.Errors import BackError, MyError, ERRORS, IGNORE, ForceError
from libs.classes.Utils import (add_member, check, is_chat, is_private,
                                promote_admin, removed_member, restrict_admin)
from libs.objects import Database, MessageData
from libs.src import system


async def test_clb(clb: t.CallbackQuery):
    await clb.answer(dp.callback_query_handlers.handlers.__len__())


# @dp.callback_query_handler(test_clb)
@dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):
    cmd = parser.Command("wtf", "Нету")
    cmd.add(
        parser.Arg(system.regex.parse.command, "command"),
        parser.Arg(system.regex.parse.reason, "reason", False),
        parser.DateArg(),
        parser.UserArg(),
    )
    args = await cmd.parse(msg)
    check = await cmd.check(msg)
    txt = f"{check}\n{'=' * 50}\n"
    for group, text in args.items():
        txt += f"{group} | {text}\n"
    await msg.answer(txt, "None")


@dp.message_handler(is_private, commands=["start"])
async def start(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    await msg.answer(src.text.private.start_text)


@system.delete_this(is_chat, state="*")
async def delete_this(clb: t.CallbackQuery):
    await clb.message.delete()


@system.back()
async def back(clb: t.CallbackQuery):
    msg = clb.message
    with await MessageData.data(msg) as data:
        try:
            history: p.List[Menu] = data.history
            history.pop(-1)
            await history[-1].edit(msg, False)
            data.history = history
        except Exception:
            raise BackError(clb.from_user.language_code)


@dp.my_chat_member_handler(add_member)
async def bot_chat_added(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.start_text)


@dp.my_chat_member_handler(removed_member)
async def bot_chat_removed(upd: t.ChatMemberUpdated):
    Database.delete_chat(upd.chat.id)


@dp.my_chat_member_handler(promote_admin)
async def bot_promote(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.promote_admin)


@dp.my_chat_member_handler(restrict_admin)
async def bot_chat_restrict(upd: t.ChatMemberUpdated):
    chat: Chat = await Chat(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.restrict_admin)


@dp.message_handler(check, content_types=[t.ContentType.TEXT, t.ContentType.PHOTO])
async def check():
    pass


@dp.errors_handler()
async def errors(upd: t.Update, error: p.Union[MyError, Exception]):
    """
    Обработчик ошибок
    """

    if error.__class__ in ERRORS:
        await error.answer(upd)
    elif error.__class__ in IGNORE:
        pass
    else:
        my_err = ForceError(f"⚠ {error.__class__.__name__}:{error.args[0]}", 0, True, False)
        await my_err.log(upd)
        await my_err.answer(upd)

    return True
