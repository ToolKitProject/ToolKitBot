import typing as p

from aiogram import types as t
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from bot import dp
from handlers.private import alias_form
from libs import filters as f
from libs.classes.Chat import Chat
from libs.classes.Errors import EmptyOwns
from libs import UserText
from libs.classes.Settings import DictSettings, Settings
from libs.classes.User import User
from libs.classes import Utils as u
from libs.objects import MessageData
from libs.src import buttons

s = buttons.private.settings
alias_data = CallbackData("alias", "key")


@dp.message_handler(u.write_action, f.message.is_private, commands=["settings"])
async def settings_cmd(msg: t.Message):
    src = UserText()
    await src.buttons.private.settings.settings.send()


# @s.private_settings(f.message.is_private)
# async def private_settings(clb: t.CallbackQuery):
#     src = UserText()
#     user = await User.create()
#     await src.buttons.private.settings.private.private_settings.get_menu(user.settings).send(clb.message)


@s.chat_settings(f.message.is_private)
async def chat_settings(clb: t.CallbackQuery):
    src = UserText()

    await clb.message.edit_text(src.text.private.settings.chat_loading)

    user = await User.create()
    chats = await user.get_owns()

    if not chats:
        await src.buttons.private.settings.settings.edit(False)
        raise EmptyOwns()

    if not chats:
        await clb.message.delete()
        raise EmptyOwns()

    menu = src.buttons.private.settings.chat.chats.copy
    for chat in chats:
        chat_settings = src.buttons.private.settings.chat.chat_settings.copy
        settings = chat_settings.get_menu(chat.settings.row, chat.id, src.lang, text=chat.title)
        settings.storage["settings"] = chat_settings
        settings.storage["chat"] = chat

        menu.add(settings)

    await menu.edit(clb.message)


@s.chat.add_alias(f.message.is_private)
async def add_alias_button(clb: t.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["settings_message"] = clb.message
    with await MessageData.data(clb.message) as data:
        element: DictSettings = data.current_element

    if element.key == "sticker_alias":
        await alias_form.start_sticker(clb)
    elif element.key == "text_alias":
        await alias_form.start_text(clb)


@dp.callback_query_handler(f.message.is_private, alias_data.filter())
async def delete_alias_button(clb: t.CallbackQuery, callback_data: p.Dict[str, str]):
    src = UserText()
    with await MessageData.data(clb.message) as data:
        data.key = callback_data["key"]

    await src.buttons.private.settings.chat.delete.edit(False)


@s.chat.delete_yes(f.message.is_private)
async def add_alias_button(clb: t.CallbackQuery):
    with await MessageData.data(clb.message) as data:
        settings: Settings = data.settings
        element: DictSettings = data.current_element
        chat: Chat = data.chat
        key: str = data.key
    element.settings.pop(key)
    menu = element.update_buttons()
    settings.save(chat)

    await menu.edit(False)
