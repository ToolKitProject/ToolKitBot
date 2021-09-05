from aiogram import types as t
from aiogram.dispatcher import FSMContext

from src import text
from src.system import states


async def start_command(clb: t.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["_message"] = clb.message

    await clb.message.edit_text(text.private.settings.report_command)
    await states.set_report_command.command.set()


async def start_count(clb: t.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["_message"] = clb.message

    await clb.message.edit_text(text.private.settings.report_count)
    await states.set_report_count.count.set()


async def start_delta(clb: t.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["_message"] = clb.message

    await clb.message.edit_text(text.private.settings.report_delta)
    await states.set_report_delta.delta.set()
