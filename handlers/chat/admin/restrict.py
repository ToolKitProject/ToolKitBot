from aiogram import types as t

from bot import dp
from libs import system
from libs.classes.Utils import (alias, bot_has_permission, get_help,
                                has_permission, is_chat, is_reply)
from libs.src import buttons


@dp.message_handler(is_chat, is_reply, alias, bot_has_permission("can_restrict_members"),
                    has_permission("can_restrict_members"), content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_command(msg: t.Message):
    pass


@dp.message_handler(is_chat, get_help, bot_has_permission("can_restrict_members"),
                    has_permission("can_restrict_members"), commands=system.restrict_commands)
async def command(msg: t.Message):
    pass


@buttons.chat.admin.undo(is_chat, has_permission("can_delete_messages"))
async def undo(clb: t.CallbackQuery):
    pass


async def execute_action():
    pass


async def get_text():
    pass
