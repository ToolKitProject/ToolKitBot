import re
from copy import deepcopy as copy
from typing import *

from aiogram import types as t
from aiogram.dispatcher.storage import FSMContext
from bot import dp
from libs.classes import AdminCommandParser, Button, Chat
from libs.classes import Errors as e
from libs.classes import User, UserText
from libs.classes.Utils import msg, is_private
from libs.objects import MessageData
from libs.src import buttons, system
from libs.src.system import regex, states


async def get_alias_menu(msg: t.Message, type: str, src: UserText, update: bool = False):
    settings = copy(src.buttons.private.settings.alias_menu)
    with await MessageData(msg) as data:
        data.type = type
        chat: Chat = await Chat(data.chat.id) if update else data.chat

        if type not in chat.settings:
            chat.settings[type] = {}
            chat.settings = chat.settings
        aliases = chat.settings[type]
        data.aliases = aliases

        for id, alias in enumerate(aliases):
            value = aliases[alias]
            if type == "command_alias":
                text = f"{alias} ➡ {value}"
            else:
                text = f"{value}"
            button = Button(text, f"alias@{id}")
            settings.add(button)
    return settings


async def get_chat_menu(msg: t.Message, user: User):
    if not user.owns:
        raise e.EmptyOwns(user.lang)
    else:
        await msg.edit_text(user.src.text.private.settings.chat_loading)

    chats = {}

    settings = copy(user.src.buttons.private.settings.chats_menu)
    for chat in await user.get_owns():
        button = Button(chat.title, f"settings@{chat.id}")
        settings.add(button)
        chats[chat.id] = chat

    with await MessageData(msg) as data:
        data.chats = chats

    return settings


@dp.message_handler(is_private, commands=["settings"])
async def settings_command(msg: t.Message):
    buttons = UserText(msg.from_user.language_code).buttons.private.settings
    await buttons.settings.send(msg)


@buttons.private.settings.chats.set_action(is_private)
async def chat_menu(clb: t.CallbackQuery):
    msg = clb.message
    user: User = await User(clb.from_user)
    settings = await get_chat_menu(msg, user)
    await settings.edit(msg)


@dp.callback_query_handler(is_private, msg(regex.settings.chat_settings))
async def chat_settings(clb: t.CallbackQuery):
    msg = clb.message
    id = int(re.match(regex.settings.chat_settings, clb.data).group("id"))

    src = UserText(clb.from_user.language_code)
    settings = src.buttons.private.settings.chat_settings
    await settings.edit(msg)

    with await MessageData(msg) as data:
        data.chat = data.chats[id]


@buttons.private.settings.sticker_alias.set_action(is_private)
@buttons.private.settings.command_alias.set_action(is_private)
async def alias_menu(clb: t.CallbackQuery):
    msg = clb.message
    type = re.match(regex.settings.data, clb.data).group("type")
    src = UserText(clb.from_user.language_code)
    settings = await get_alias_menu(msg, type, src)
    await settings.edit(msg)


@dp.callback_query_handler(is_private, msg(regex.settings.alias_delete))
async def del_alias(clb: t.CallbackQuery):
    msg = clb.message
    buttons = UserText(clb.from_user.language_code).buttons.private.settings
    id = int(re.match(regex.settings.alias_delete, clb.data).group("id"))
    with await MessageData(msg) as data:
        aliases: Dict[str, str] = data.aliases
        data.key = list(aliases.keys())[id]

    await buttons.delete_title.edit(msg, False)


@buttons.private.settings.delete_accept.set_action(is_private)
@buttons.private.settings.delete_cancel.set_action(is_private)
async def del_confirm(clb: t.CallbackQuery):
    msg = clb.message
    src = UserText(clb.from_user.language_code)
    with await MessageData(msg) as data:
        if clb.data == "delete_accept":
            aliases: dict = data.aliases
            aliases.pop(data.key)
            chat: Chat = data.chat
            chat.settings[data.type] = aliases
            chat.settings = chat.settings
        settings = await get_alias_menu(msg, data.type, src, True)
    await settings.edit(msg, False)


@buttons.private.settings.add_alias.set_action(is_private)
async def add_alias(clb: t.CallbackQuery, state: FSMContext):
    msg = clb.message
    src = UserText(clb.from_user.language_code)
    with await MessageData(msg) as data:
        type: str = data.type
        aliases = data.aliases

    if type == "sticker_alias":
        # , reply_markup=back.inline
        await msg.edit_text(src.text.private.settings.sticker)
    else:
        await msg.edit_text(src.text.private.settings.text)

    await states.add_alias.alias.set()
    async with state.proxy() as proxy:
        proxy["msg"] = msg
        proxy["type"] = type
        proxy["aliases"] = aliases


# @back.set_action(is_private, state=[states.add_alias.alias, states.add_alias.command])
@dp.message_handler(is_private, commands=["cancel"], state=[states.add_alias.alias, states.add_alias.command])
async def cancel(clb: t.CallbackQuery, state: FSMContext):
    src = UserText(clb.from_user.language_code)
    async with state.proxy() as proxy:
        settings_msg = proxy["msg"]
        type = proxy["type"]

    await state.finish()
    settings = await get_alias_menu(settings_msg, type, src, True)
    if clb.__class__ == t.CallbackQuery:
        await settings.edit(clb.message)
    else:
        msg = await settings.send(settings_msg)
        await MessageData.move(msg, settings_msg)


@dp.message_handler(is_private, content_types=[t.ContentType.STICKER, t.ContentType.TEXT], state=states.add_alias.alias)
async def alias(msg: t.Message, state: FSMContext):
    src = UserText(msg.from_user.language_code)
    async with state.proxy() as proxy:
        aliases = proxy["aliases"]
        alias: str = ""
        if msg.sticker and proxy["type"] == "sticker_alias":
            alias = msg.sticker.file_unique_id
        elif msg.text and proxy["type"] == "command_alias":
            alias = msg.text
        else:
            await msg.delete()
            raise e.TypeError(src.lang, 3)

        if alias in aliases:
            await msg.delete()
            raise e.AlreadyExists(src.lang, 3)
        else:
            proxy["alias"] = alias

        msg = proxy["msg"]
        await msg.answer(src.text.private.settings.command)
    await states.add_alias.next()


@dp.message_handler(is_private, commands=system.restrict_commands, state=states.add_alias.command)
async def sticker(msg: t.Message, state: FSMContext):
    src = UserText(msg.from_user.language_code)

    async with state.proxy() as proxy:
        type = proxy["type"]
        settings_msg = proxy["msg"]

        chek = await AdminCommandParser.chek(msg.text, "user", "id")
        if not chek:
            await msg.delete()
            raise e.ArgumentError(src.lang, 3)

        with await MessageData(settings_msg) as data:
            chat: Chat = data.chat
        chat.settings[type][proxy["alias"]] = msg.text
        chat.settings = chat.settings

    await state.finish()
    settings = await get_alias_menu(settings_msg, type, src, True)
    msg = await settings.send(settings_msg)
    await MessageData.move(msg, settings_msg)


@dp.message_handler(is_private, content_types=t.ContentType.ANY, state=[states.add_alias.alias, states.add_alias.command])
async def any_delete(msg: t.Message):
    await msg.delete()
    raise e.TypeError(msg.from_user.language_code, 3)
