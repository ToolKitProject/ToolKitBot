import re
import typing as p

from aiogram import types as t, filters as f, Bot

from bot import bot
from libs.classes import Errors as e
from libs.objects import Database
from libs.system import regex as r

objType = p.Union[t.Message, t.CallbackQuery, t.ChatMemberUpdated]


class _helper:
    @staticmethod
    def get_user_and_chat(obj: objType):
        if isinstance(obj, t.Message):
            chat = obj.chat
            user = obj.from_user
        elif isinstance(obj, t.CallbackQuery):
            chat = obj.message.chat
            user = obj.from_user
        elif isinstance(obj, t.ChatMemberUpdated):
            chat = obj.chat
            user = obj.from_user
        else:
            raise TypeError()

        return user, chat

    @staticmethod
    def has_permission(admin: t.ChatMember, permission: str):
        if t.ChatMemberStatus.is_chat_creator(admin.status):
            return True
        elif t.ChatMemberStatus.is_chat_admin(admin.status):
            return getattr(admin, permission)
        else:
            return False


class AdminFilter(f.BoundFilter):
    def __init__(self, user_id: int = None):
        self._user_id = user_id

    async def check(self, obj: objType):
        user, chat = _helper.get_user_and_chat(obj)

        admin = await chat.get_member(self._user_id or user.id)
        if t.ChatMemberStatus.is_chat_admin(admin.status):
            return True
        else:
            return False


class AliasFilter(f.BoundFilter):
    def __init__(self):
        pass

    async def check(self, msg: objType) -> bool:
        if not isinstance(msg, t.Message):
            raise TypeError()
        if await message.is_private.check(msg):
            return False
        chat = Database.get_chat(msg.chat.id)

        if msg.sticker:
            aliases = list(chat.settings.sticker_alias.keys())
            text = msg.sticker.file_unique_id
        elif msg.text:
            aliases = list(chat.settings.text_alias.keys())
            text = msg.text

        for alias in aliases:
            pattern = re.compile(r.alias(alias), re.IGNORECASE)
            if pattern.match(text):
                return True

        return False


class message:
    is_chat = f.ChatTypeFilter((t.ChatType.GROUP, t.ChatType.SUPERGROUP))
    is_private = f.ChatTypeFilter(t.ChatType.PRIVATE)
    is_reply = f.IsReplyFilter(True)
    is_alias = AliasFilter()


class bot:
    is_admin = AdminFilter(bot.id)

    @staticmethod
    def has_permission(permissions: p.List[str]):
        permissions = permissions

        async def filter(obj: objType):
            bot = Bot.get_current()
            user, chat = _helper.get_user_and_chat(obj)
            admin = await chat.get_member(bot.id)
            if not _helper.has_permission(admin, permissions):
                raise e.BotHasNotPermission()
            return True

        return filter


class user:
    is_admin = AdminFilter()

    @staticmethod
    def has_permission(permissions: p.List[str]):
        permissions = permissions

        async def filter(obj: objType):
            user, chat = _helper.get_user_and_chat(obj)
            admin = await chat.get_member(user.id)
            if not _helper.has_permission(admin, permissions):
                raise e.HasNotPermission()
            return True

        return filter

    @staticmethod
    def add_member(upd: t.ChatMemberUpdated):
        old = upd.old_chat_member
        new = upd.new_chat_member
        return not t.ChatMemberStatus.is_chat_member(old.status) and t.ChatMemberStatus.is_chat_member(new.status)

    @staticmethod
    def removed_member(upd: t.ChatMemberUpdated):
        old = upd.old_chat_member
        new = upd.new_chat_member
        return t.ChatMemberStatus.is_chat_member(old.status) and not t.ChatMemberStatus.is_chat_member(new.status)

    @staticmethod
    def promote_admin(upd: t.ChatMemberUpdated):
        old = upd.old_chat_member
        new = upd.new_chat_member
        return not t.ChatMemberStatus.is_chat_admin(old.status) and t.ChatMemberStatus.is_chat_admin(new.status)

    @staticmethod
    def restrict_admin(upd: t.ChatMemberUpdated):
        old = upd.old_chat_member
        new = upd.new_chat_member
        return t.ChatMemberStatus.is_chat_admin(old.status) and not t.ChatMemberStatus.is_chat_admin(new.status)
