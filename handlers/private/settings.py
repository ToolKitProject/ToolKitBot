import re
from copy import deepcopy as copy
from typing import *

from aiogram import types as t
from bot import dp
from libs.classes import Button, Chat, User, UserText, clb, is_private
from libs.objects import MessageData
from libs.src import buttons
from libs.src.system import regex


@dp.message_handler(is_private, commands=["settings"])
async def settings(msg: t.Message):
    buttons = UserText(msg.from_user.language_code).buttons.private.settings
    await buttons.settings.answer(msg)


@buttons.private.settings.chats.set_action(is_private)
async def chats(clb: t.CallbackQuery):
    msg = clb.message
    src = UserText(clb.from_user.language_code)
    settings = src.buttons.private.settings
    user: User = await User(user=clb.from_user)

    if not user.owns:
        await clb.answer(src.text.private.settings.empty)
        return

    await clb.answer(src.text.private.settings.chat_loading)

    menu = copy(settings.chats_menu)
    chats = await user.get_owns()
    for chat in chats:
        button = Button(chat.title, f"settings@{chat.id}")
        menu.add(button)

    await menu.edit(msg)

    with await MessageData(msg) as data:
        data.chats = chats


@dp.callback_query_handler(is_private, clb(regex.settings.chat_settings))
async def chat(clb: t.CallbackQuery):
    msg = clb.message
    src = UserText(clb.from_user.language_code)
    settings = src.buttons.private.settings.chat_settings
    id = int(re.match(regex.settings.chat_settings, clb.data).group("id"))
    with await MessageData(msg) as data:
        chat: Chat
        for chat in data.chats:
            if chat.id == id:
                data.chat = chat

    await settings.edit(msg)


async def add_alias(msg: t.Message, chat: Chat):
    pass
