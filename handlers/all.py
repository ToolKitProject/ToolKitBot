import typing as p

from aiogram import types as t

import src
from libs import errors as e
from libs.buttons import Menu
from libs.commandParser import ParsedArgs
from src.objects import MessageData
from src import other, filters as f


@other.parsers.help()
async def help(msg: t.Message, parsed: ParsedArgs):  # help command
    cmd: str = parsed.cmd
    text = None
    if not cmd:  # if not search command
        if await f.message.is_chat.check(msg):  # if chat
            if await f.user.is_admin.check(msg):  # if member admin
                text = str(other.command_list.get_group(t.BotCommandScopeAllChatAdministrators()))
            else:
                text = str(other.command_list.get_group(t.BotCommandScopeAllGroupChats()))
        elif await f.message.is_private.check(msg):  # if private chat
            text = str(other.command_list.get_group(t.BotCommandScopeAllPrivateChats()))
    else:
        command = other.command_list.get(cmd.removeprefix("/"))
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
    try:
        with MessageData.data() as data:
            history: p.List[Menu] = data.history
            while True:
                history.pop(-1)
                try:
                    await history[-1].edit(False)
                except Exception:
                    continue
                else:
                    break

            data.history = history
    except Exception:
        raise e.BackError()
