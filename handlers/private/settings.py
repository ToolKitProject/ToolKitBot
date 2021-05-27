from copy import deepcopy

from aiogram import types as t

from bot import dp
from libs.classes import UserText, User, Settings, Chat
from libs.classes.Errors import EmptyOwns
from libs.classes.Utils import is_private
from libs.objects import MessageData, Database
from libs.src import buttons

s = buttons.private.settings


@dp.message_handler(is_private, commands=["settings"])
async def settings(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    await src.buttons.private.settings.settings.send(msg)


@s.chat_list()
async def chat_list(clb: t.CallbackQuery):
    src = UserText(clb.from_user.language_code)

    owns = Database.get_owns(clb.from_user.id)
    if not owns:
        raise EmptyOwns(src.lang)
    await clb.message.edit_text(src.text.private.settings.chat_loading)

    user: User = await User(clb.from_user)
    chats = user.iter_owns()

    menu = deepcopy(src.buttons.private.settings.chats)
    chat_settings = src.buttons.private.settings.chat_settings
    async for chat in chats:
        button = chat_settings.menu(chat.settings, text=chat.title, key=chat.id)

        @button.set_middleware()
        async def button_middleware(clb_middleware: t.CallbackQuery, _):
            with await MessageData.state(clb_middleware.message) as data:
                data.chat = chat
                data.settings = chat_settings
            return True

        menu.add(button)

    await menu.edit(clb.message)


@s.add_alias()
async def chat_list(clb: t.CallbackQuery):
    with await MessageData.state(clb.message) as data:
        chat: Chat = data.chat
        chat_settings: Settings = data.settings

    chat_settings.save(chat)
