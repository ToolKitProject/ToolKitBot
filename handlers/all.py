import typing as p

from aiogram import types as t
from aiogram.dispatcher import FSMContext

from bot import dp
from libs import errors as e
from libs.buttons import Menu
from libs.command_parser import ParsedArgs
from libs.settings import Property, SettingsType
from src.instances import MessageData
from src import filters as f
from locales import other
from src.states import states


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


@locales.buttons.delete_this(state="*")
async def delete_this(clb: t.CallbackQuery):
    """
    *delete_this* button handler
    """
    await MessageData.delete(clb.message, False)


@locales.buttons.back(state="*")
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


@dp.message_handler(f.message.is_private, commands=["cancel"], state="*")
async def cancel(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["_message"]
    with MessageData.data(from_msg) as data:
        prop: Property = data.property
        settings: SettingsType = data.settings

    to_msg = await prop.menu(settings).send()
    await MessageData.move(from_msg, to_msg)
    await states.add_alias.finish()
