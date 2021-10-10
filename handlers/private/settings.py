from aiogram import types as t
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

import handlers.all
from bot import dp
from libs.buttons import Submenu
from libs.chat import Chat
from libs.errors import EmptyOwns
from libs.settings import Property, SettingsType
from libs.user import User
from locales import text, buttons
from src import filters as f, utils as u, stages
from src.instances import MessageData
from src.utils import save_target_settings, get_key_by_id

s = buttons.private.settings
alias_data = CallbackData("delete_alias", "id")
lang_data = CallbackData("change_lang", "lang")
statistic_data = CallbackData("statistic", "mode")
set_report_delta = CallbackData("set_report_delta", "delta")


@dp.message_handler(u.write_action, f.message.is_private, commands=["settings"])
async def settings_cmd(msg: t.Message):
    await buttons.private.settings.settings.send()


@s.private_settings(f.message.is_private)
async def private_settings(clb: t.CallbackQuery):
    user = await User.create(clb.from_user)
    with MessageData.data() as data:
        data.target = user
    await buttons.private.settings.private.settings.menu(user.settings).edit()


@s.chat_settings(f.message.is_private)
async def chat_settings(clb: t.CallbackQuery):
    user = await User.create(clb.from_user)
    await clb.message.edit_text(text.private.settings.chat_loading)
    chats = await user.get_owns()

    if not chats:
        await EmptyOwns().answer()
        await clb.message.delete()
        await buttons.private.settings.settings.send()
        return

    menu = buttons.private.settings.chat_list.copy
    for chat in chats:
        s = chat.settings
        settings = buttons.private.settings.chat.settings.menu(s, text=chat.title, callback_data=chat.id)
        settings.storage["target"] = chat
        menu.add(settings)
    await menu.edit()


@buttons.add_alias(f.message.is_private)
async def add_alias(clb: t.CallbackQuery, state: FSMContext):
    with MessageData.data() as data:
        prop: Property = data.property

    if prop.key == "sticker_alias":
        await stages.add_alias.sticker.set()
    elif prop.key == "text_alias":
        await stages.add_alias.text.set()


@buttons.set_report_count(f.message.is_private)
@buttons.set_report_command(f.message.is_private)
@buttons.set_report_delta(f.message.is_private)
async def start_report_form(clb: t.CallbackQuery):
    type = clb.data
    if type == "set_report_command":
        await stages.set_report_command.command.set()
    elif type == "set_report_count":
        await stages.set_report_count.count.set()
    elif type == "set_report_delta":
        await stages.set_report_delta.delta.set()


@dp.callback_query_handler(f.message.is_private, alias_data.filter())
async def delete_alias(clb: t.CallbackQuery, callback_data: dict[str, str]):
    with MessageData.data() as data:
        data.key = get_key_by_id(data.settings, callback_data["id"])
    await buttons.delete.edit()


@buttons.delete_yes(f.message.is_private)
async def delete_yes(clb: t.CallbackQuery):
    with MessageData.data() as data:
        settings: SettingsType = data.settings
        target: Chat | User = data.target
        prop: Property = data.property
        menu: Submenu = data.menu
        key = data.key

    settings.pop(key)
    menu.update(prop.menu(settings))
    await menu.edit(False)

    save_target_settings(target)


@dp.callback_query_handler(f.message.is_private, lang_data.filter())
async def edit_lang(clb: t.CallbackQuery, callback_data: dict[str, str]):
    with MessageData.data() as data:
        settings: SettingsType = data.settings
        target: Chat | User = data.target

    settings["lang"] = callback_data["lang"]
    save_target_settings(target)
    await handlers.all.back(clb)


@dp.callback_query_handler(f.message.is_private, statistic_data.filter())
async def statistic_change(clb: t.CallbackQuery, callback_data: dict[str, str]):
    with MessageData.data() as data:
        settings: SettingsType = data.settings
        target: Chat | User = data.target
        menu: Submenu = data.menu

    settings["mode"] = int(callback_data["mode"])
    save_target_settings(target)

    await clb.answer(text.private.settings.statistic_mode_changed)
    await menu.edit(False)


@buttons.statistic_title.format_callback()
@text.private.settings.statistic_mode_changed.format_callback()
def format_callback(txt: str):
    with MessageData.data() as data:
        target: Chat | User = data.target
    return txt.format(mode=str(text.statistic_modes[target.statistic_mode]))


@text.private.settings.report_command.format_callback()
def format_report_command(txt: str):
    with MessageData.data() as data:
        target: Chat = data.target
    return txt.format(command=target.report_command)


@text.private.settings.report_count.format_callback()
def format_report_count(txt: str):
    with MessageData.data() as data:
        target: Chat = data.target
    return txt.format(count=target.report_count)


@text.private.settings.report_delta.format_callback()
def format_report_delta(txt: str):
    with MessageData.data() as data:
        target: Chat = data.target
    return txt.format(delta=target.report_delta.days)
