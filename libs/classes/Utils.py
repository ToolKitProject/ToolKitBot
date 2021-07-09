import re
import typing as p

from aiogram import types as t
from aiogram.dispatcher import filters as f

import config as c
from bot import bot
from libs.objects import Database
from . import Errors as e
from .Chat import Chat
from .Localisation import UserText
from .User import User

is_chat = f.ChatTypeFilter((t.ChatType.GROUP, t.ChatType.SUPERGROUP))
is_private = f.ChatTypeFilter(t.ChatType.PRIVATE)
is_reply = f.IsReplyFilter(True)


def lower_dict(d: p.Dict[str, p.Any]):
    result = {}
    for key, value in d.items():
        result[key.lower()] = value
    return result


def find_key(d: p.Dict[str, p.Any], key: str):
    for k in d.keys():
        if k.lower() == key.lower():
            return k
    return key


async def get_help(msg: t.Message):
    """
    Отправка help текста нужной локализации
    """
    if await is_reply.check(msg):
        return True
    if not msg.get_args():
        await mark_write(msg)
        command = msg.get_command(True)
        src = UserText(msg.from_user.language_code)

        try:
            text = getattr(src.text.help, command)
            await msg.reply(text, disable_web_page_preview=True)
            return False
        except:
            pass
    return True


async def mark_write(msg: t.Message):
    await msg.answer_chat_action(t.ChatActions.TYPING)
    return True


def add_member(upd: t.ChatMemberUpdated):
    old = upd.old_chat_member
    new = upd.new_chat_member
    return not t.ChatMemberStatus.is_chat_member(old.status) and t.ChatMemberStatus.is_chat_member(new.status)


def removed_member(upd: t.ChatMemberUpdated):
    old = upd.old_chat_member
    new = upd.new_chat_member
    return t.ChatMemberStatus.is_chat_member(old.status) and not t.ChatMemberStatus.is_chat_member(new.status)


def promote_admin(upd: t.ChatMemberUpdated):
    old = upd.old_chat_member
    new = upd.new_chat_member
    return not t.ChatMemberStatus.is_chat_admin(old.status) and t.ChatMemberStatus.is_chat_admin(new.status)


def restrict_admin(upd: t.ChatMemberUpdated):
    old = upd.old_chat_member
    new = upd.new_chat_member
    return t.ChatMemberStatus.is_chat_admin(old.status) and not t.ChatMemberStatus.is_chat_admin(new.status)


def bot_has_permission(*permissions: str):
    async def filter(msg: t.Message):
        member = await bot.get_chat_member(msg.chat.id, c.bot.id)
        if member.status != t.ChatMemberStatus.ADMINISTRATOR:
            raise e.BotHasNotPermission(msg.from_user.language_code)
        for permission in permissions:
            if not getattr(member, permission):
                raise e.BotHasNotPermission(msg.from_user.language_code)
        return True

    return filter


def has_permission(*permissions: str):
    async def filter(msg: p.Union[t.Message, t.CallbackQuery]):
        if isinstance(msg, t.Message):
            member = await msg.chat.get_member(msg.from_user.id)
        elif isinstance(msg, t.CallbackQuery):
            member = await msg.message.chat.get_member(msg.from_user.id)
        else:
            return TypeError("has_permission не там стоит")

        if not t.ChatMemberStatus.is_chat_admin(member.status):
            raise e.HasNotPermission(member.user.language_code)
        elif member.status == t.ChatMemberStatus.ADMINISTRATOR:
            for perm in permissions:
                if not getattr(member, perm):
                    raise e.HasNotPermission(member.user.language_code)
        return True

    return filter


def msg(data):
    pattern = re.compile(data)

    async def filter(clb: t.CallbackQuery):
        if pattern.match(clb.data):
            return True
        return False

    return filter


async def alias(msg: t.Message, handler=True) -> p.Union[bool, str]:
    chat = Database.get_chat(msg.chat.id)
    if msg.sticker:
        text = msg.sticker.file_unique_id
        aliases = chat.settings.sticker_alias
    elif msg.text:
        text = msg.text.lower()
        aliases = lower_dict(chat.settings.text_alias)

    if handler:
        return text in aliases
    else:
        return aliases[text]


async def check(msg: t.Message):
    if await is_chat.check(msg) and not Database.get_chat(msg.chat.id):
        await Chat.create(msg.chat)
    if not Database.get_user(msg.from_user.id):
        await User.create(msg.from_user)

    return False
