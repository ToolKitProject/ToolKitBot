import typing as p

from aiogram import types as t
from aiogram.dispatcher import FSMContext

import handlers
from libs import errors as e
from libs.chat import Chat
from libs.settings import SettingsType
from libs.user import User
from src import filters as f
from src import stages
from src.commands import alias_commands
from src.instances import MessageData
from src.utils import save_target_settings


@stages.add_alias.sticker(f.message.is_private, content_types=[t.ContentType.STICKER])
async def sticker_form(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        data["key"] = msg.sticker.file_unique_id
    await stages.add_alias.command.set()


@stages.add_alias.text(f.message.is_private, content_types=[t.ContentType.TEXT])
async def text_form(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        data["key"] = msg.text
    await stages.add_alias.command.set()


@stages.add_alias.command(f.message.is_private, commands=alias_commands)
async def command_form(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["_message"]
        key: str = data["key"]
        value: str = msg.text
    with MessageData.data(from_msg) as data:
        settings: SettingsType = data.settings
        target: p.Union[Chat, User] = data.target

    settings[key] = value
    save_target_settings(target)

    await handlers.all.cancel(msg, state)


@stages.add_alias.text(f.message.is_private, content_types=t.ContentType.ANY)
async def text_supported_error(msg: t.Message):
    raise e.FormTypeError.FormTextSupported()


@stages.add_alias.sticker(f.message.is_private, content_types=t.ContentType.ANY)
async def sticker_supported_error(msg: t.Message):
    raise e.FormTypeError.FormStickerSupported()


@stages.add_alias.command(f.message.is_private, content_types=t.ContentType.ANY)
async def sticker_supported_error(msg: t.Message):
    raise e.FormTypeError.FormCommandNotSupported()
