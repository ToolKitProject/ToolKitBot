import typing as p

from aiogram import types as t

from bot import dp, bot
from libs import system, src
from libs.classes.Buttons import Menu
from libs.classes import Errors as e
from libs import UserText
from libs.objects import MessageData
from libs.src import any
from libs import filters as f


@dp.message_handler(commands=["fix"])
async def fix_commands(msg: t.Message, send: bool = True):
    """
    Fixes broken hints for commands
    """
    for lang in lang_conf.lang_map:  # Delete commands for current chat and all locales
        if lang == "other":
            lang = None
        await bot.delete_my_commands(t.BotCommandScopeChat(msg.chat.id), lang)

    if send:
        src = UserText()
        await msg.answer(src.text.chat.fix_commands)


@any.parsers.help()
async def help(msg: t.Message):  # help command
    src = UserText()
    parsed = await src.any.parsers.help.parse(msg)
    cmd: str = parsed.cmd
    if not cmd:  # if not search command
        if await f.message.is_chat.check(msg):  # if chat
            if await f.user.is_admin.check(msg):  # if member admin
                text = str(src.any.command_list.get_group(t.BotCommandScopeAllChatAdministrators()))
            else:
                text = str(src.any.command_list.get_group(t.BotCommandScopeAllGroupChats()))
        elif await f.message.is_private.check(msg):  # if private chat
            text = str(src.any.command_list.get_group(t.BotCommandScopeAllPrivateChats()))
    else:
        command = src.any.command_list.get(cmd.removeprefix("/"))
        if not command:  # if command not found
            raise e.CommandNotFound()
        text = str(command)
    await msg.answer(text, disable_web_page_preview=True)


@src.buttons.delete_this(state="*")
async def delete_this(clb: t.CallbackQuery):
    """
    *delete_this* button handler
    """
    await MessageData.delete(clb.message, False)


@src.buttons.back(state="*")
async def back(clb: t.CallbackQuery):
    """
    *back* button handler
    """
    msg = clb.message
    with await MessageData.data(msg) as data:
        try:
            history: p.List[Menu] = data.history
            history.pop(-1)
            await history[-1].edit(False)
            data.history = history
        except Exception:
            raise e.BackError()
