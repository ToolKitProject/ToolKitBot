from aiogram import types as t
from aiogram.dispatcher import FSMContext

from bot import dp
from libs import errors as e
from libs.buttons import Submenu
from libs.chat import Chat
from libs.settings import Property, SettingsType
from src.objects import MessageData
from src.system import alias_commands
from src.system import states
from src import text, filters as f


async def start_sticker(clb: t.CallbackQuery):
    await clb.message.edit_text(text.private.settings.sticker)
    await states.add_alias.sticker.set()


async def start_text(clb: t.CallbackQuery):
    await clb.message.edit_text(text.private.settings.text)
    await states.add_alias.text.set()


@dp.message_handler(f.message.is_private, content_types=[t.ContentType.STICKER], state=states.add_alias.sticker)
async def sticker_form(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        data["key"] = msg.sticker.file_unique_id
    await msg.answer(text.private.settings.command)
    await states.add_alias.command.set()


@dp.message_handler(f.message.is_private, content_types=[t.ContentType.TEXT], state=states.add_alias.text)
async def text_form(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        data["key"] = msg.text
    await msg.answer(text.private.settings.command)
    await states.add_alias.command.set()


@dp.message_handler(f.message.is_private, commands=alias_commands, state=states.add_alias.command)
async def command_form(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["settings_message"]
        key: str = data["key"]
        value: str = msg.text
    with MessageData.data(from_msg) as data:
        settings: SettingsType = data.settings
        prop: Property = data.property
        menu: Submenu = data.menu
        chat: Chat = data.chat

    settings[key] = value
    chat.chatOBJ.settings = chat.settings

    menu.update(prop.menu(settings))
    to_msg = await menu.send()
    await MessageData.move(from_msg, to_msg)
    await states.add_alias.finish()


@dp.message_handler(f.message.is_private, content_types=t.ContentType.ANY, state=states.add_alias.text)
async def text_supported_error(msg: t.Message):
    raise e.AliasTypeError.AliasTextSupported()


@dp.message_handler(f.message.is_private, content_types=t.ContentType.ANY, state=states.add_alias.sticker)
async def sticker_supported_error(msg: t.Message):
    raise e.AliasTypeError.AliasStickerSupported()


@dp.message_handler(f.message.is_private, content_types=t.ContentType.ANY, state=states.add_alias.command)
async def sticker_supported_error(msg: t.Message):
    raise e.AliasTypeError.AliasCommandNotSupported()
