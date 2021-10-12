from __future__ import annotations

from aiogram import types as t
from aiogram.dispatcher import FSMContext

import handlers
from bot import dp
from libs import errors as e
from libs.chat import Chat
from libs.settings import SettingsType
from libs.user import User
from locales.other import parsers
from main import MessageData
from src import filters as f
from src import stages
from src.commands import set_report_commands
from src.utils import save_target_settings


@stages.set_report_command.command(f.message.is_private, commands=set_report_commands)
async def report_command(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["_message"]
    with MessageData.data(from_msg) as data:
        settings: SettingsType = data.settings
        target: Chat | User = data.target

    settings["command"] = f"/{msg.get_command(True)} {msg.get_args()}".strip()
    save_target_settings(target)

    await handlers.all.cancel(msg, state)


@stages.set_report_count.count(f.message.is_private, content_types=[t.ContentType.TEXT])
async def report_count(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["_message"]
    with MessageData.data(from_msg) as data:
        settings: SettingsType = data.settings
        target: Chat | User = data.target

    parsed = await parsers.report_count.parse_message(msg)
    settings["count"] = parsed.count
    save_target_settings(target)

    await handlers.all.cancel(msg, state)


@stages.set_report_delta.delta(f.message.is_private, content_types=[t.ContentType.TEXT])
async def report_delta(msg: t.Message, state: FSMContext):
    async with state.proxy() as data:
        from_msg: t.Message = data["_message"]
    with MessageData.data(from_msg) as data:
        settings: SettingsType = data.settings
        target: Chat | User = data.target

    parsed = await parsers.report_delta.parse_message(msg)
    settings["delta"] = int(parsed.delta.total_seconds())
    save_target_settings(target)

    await handlers.all.cancel(msg, state)


@dp.message_handler(f.message.is_private, state=[stages.set_report_command])
async def not_report_command(msg: t.Message, state: FSMContext):
    raise e.FormTypeError.FormCommandNotSupported()
