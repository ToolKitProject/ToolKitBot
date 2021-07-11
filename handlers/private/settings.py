import typing as p

from aiogram import types as t
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from bot import dp
from handlers.private import alias_form
from libs import filters as f
from libs.classes.Chat import Chat
from libs.classes.Errors import EmptyOwns
from libs.classes.Localisation import UserText
from libs.classes.Settings import DictSettings, Settings
from libs.classes.User import User
from libs.classes import Utils as u
from libs.objects import MessageData, Database
from libs.src import buttons

s = buttons.private.settings
alias_data = CallbackData("alias", "key")


@dp.message_handler(u.write_action, f.message.is_private, commands=["settings"])
async def settings_cmd(msg: t.Message):
    src = UserText(msg.from_user.language_code)
    await src.buttons.private.settings.settings.send(msg)


@s.chat_list(f.message.is_private)
async def chat_list_menu(clb: t.CallbackQuery):
    src = UserText(clb.from_user.language_code)

    if not Database.get_owns(clb.from_user.id):
        raise EmptyOwns(src.lang)
    await clb.message.edit_text(src.text.private.settings.chat_loading)

    user = await User.create(clb.from_user)
    chats = await user.get_owns()

    menu = src.buttons.private.settings.chats.copy
    for chat in chats:
        chat_settings = src.buttons.private.settings.chat_settings.copy
        settings = chat_settings.get_menu(chat.settings.row, chat.id, src.lang, text=chat.title)
        settings.storage["settings"] = chat_settings
        settings.storage["chat"] = chat

        menu.add(settings)

    await menu.edit(clb.message)


@s.add_alias(f.message.is_private)
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
    src = UserText(clb.from_user.language_code)
    with await MessageData.data(clb.message) as data:
        data.key = callback_data["key"]

    await src.buttons.private.settings.delete.edit(clb.message, False)


@s.delete_yes(f.message.is_private)
async def add_alias_button(clb: t.CallbackQuery):
    with await MessageData.data(clb.message) as data:
        settings: Settings = data.settings
        element: DictSettings = data.current_element
        chat: Chat = data.chat
        key: str = data.key
    element.settings.pop(key)
    menu = element.update_buttons()
    settings.save(chat)

    await menu.edit(clb.message, False)
