from aiogram import types as t
from aiogram.dispatcher import FSMContext

from bot import dp
from libs.classes import Errors as e
from libs.classes.Settings import Settings, DictSettings
from libs.classes.Chat import Chat
from libs.classes.Localisation import UserText
from libs.classes.Utils import is_private, find_key
from libs.objects import MessageData
from libs.system import restrict_commands
from libs.system import states


async def start_sticker(clb: t.CallbackQuery):
    src = UserText(clb.from_user.language_code)
    await clb.message.edit_text(src.text.private.settings.sticker)
    await states.add_alias.sticker.set()


async def start_text(clb: t.CallbackQuery):
    src = UserText(clb.from_user.language_code)
    await clb.message.edit_text(src.text.private.settings.text)
    await states.add_alias.text.set()


@dp.message_handler(is_private, commands=["cancel"], state=states.add_alias)
async def cancel(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["settings_message"]
    with await MessageData.data(from_msg) as data:
        element: DictSettings = data.current_element
        menu = element.update_buttons()

    to_msg = await menu.send(msg)
    await MessageData.move(from_msg, to_msg)
    await state.finish()


@dp.message_handler(is_private, content_types=[t.ContentType.STICKER], state=states.add_alias.sticker)
async def sticker_form(msg: t.Message, state: FSMContext):
    src = UserText(msg.from_user.language_code)
    async with state.proxy() as data:
        data["key"] = msg.sticker.file_unique_id
    await msg.answer(src.text.private.settings.command)
    await states.add_alias.command.set()


@dp.message_handler(is_private, content_types=[t.ContentType.TEXT], state=states.add_alias.text)
async def text_form(msg: t.Message, state: FSMContext):
    src = UserText(msg.from_user.language_code)
    async with state.proxy() as data:
        data["key"] = msg.text
    await msg.answer(src.text.private.settings.command)
    await states.add_alias.command.set()


@dp.message_handler(is_private, commands=restrict_commands, state=states.add_alias.command)
async def command_form(msg: t.Message, state: FSMContext):
    src = UserText(msg.from_user.language_code)

    async with state.proxy() as data:
        from_msg: t.Message = data["settings_message"]
        key: str = data["key"]
        value: str = msg.text
    with await MessageData.data(from_msg) as data:
        settings: Settings = data.settings
        element: DictSettings = data.current_element
        chat: Chat = data.chat

    check = await src.any.command.AdminCommandParser.check_types(msg, "user")
    if check:
        await msg.delete()
        raise e.ArgumentError(src.lang)

    key: str = find_key(element.settings, key)
    element.settings[key] = value
    settings.save(chat)

    menu = element.update_buttons()

    to_msg = await menu.send(msg)
    await MessageData.move(from_msg, to_msg)
    await states.add_alias.next()


@dp.message_handler(is_private, content_types=t.ContentType.ANY, state=states.add_alias)
async def any_delete(msg: t.Message):
    await msg.delete()
    raise e.TypeError(msg.from_user.language_code)
