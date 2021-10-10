from bot import dp, bot
from aiogram import types as t

from libs.chat import Chat
from src.instances import Database
from src import filters as f
from locales import text, buttons


@dp.my_chat_member_handler(f.user.add_member, f.message.is_chat)
async def bot_chat_added(upd: t.ChatMemberUpdated):
    """
    If bot added in the chat
    """
    chat: Chat = await Chat.create(upd.chat)
    await bot.send_message(chat.id, text.chat.start_text, reply_markup=buttons.chat.start_button(upd.chat.id))


@dp.my_chat_member_handler(f.user.removed_member, f.message.is_chat)
async def bot_chat_removed(upd: t.ChatMemberUpdated):
    """
    If bot removed in the chat
    """
    Database.delete_chat(upd.chat.id)


@dp.my_chat_member_handler(f.user.promote_admin, f.message.is_chat)
async def bot_promote(upd: t.ChatMemberUpdated):
    """
    If bot promote to admin
    """
    chat: Chat = await Chat.create(upd.chat)
    await bot.send_message(chat.id, text.chat.promote_admin)


@dp.my_chat_member_handler(f.user.restrict_admin, f.message.is_chat)
async def bot_chat_restrict(upd: t.ChatMemberUpdated):
    """
    If bot restrict to admin
    """
    chat: Chat = await Chat.create(upd.chat)
    await bot.send_message(chat.id, text.chat.restrict_admin)
