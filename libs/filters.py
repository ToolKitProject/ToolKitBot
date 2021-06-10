from aiogram import types as t, filters as f
from bot import dp
import typing as p

import config

objType = p.Union[t.Message, t.CallbackQuery, t.ChatMemberUpdated]


class _helper:
    @staticmethod
    def get_user_and_chat(obj: objType):
        user, chat = None, None
        if isinstance(obj, t.Message):
            chat = obj.chat
            user = obj.from_user
        elif isinstance(obj, t.CallbackQuery):
            chat = obj.message.chat
            user = obj.from_user
        elif isinstance(obj, t.ChatMemberUpdated):
            chat = obj.chat
            user = obj.from_user
        return user, chat

    @staticmethod
    def has_permission(admin: t.ChatMember, permissions: p.Set[str]):
        if admin.is_chat_creator():
            return True
        elif admin.is_chat_admin():
            for perm in permissions:
                if not getattr(admin, perm):
                    return False
            return True
        else:
            return False


class AdminFilter(f.BoundFilter):
    def __init__(self, user_id: int = None):
        self._user_id = user_id

    async def check(self, obj: objType):
        user, chat = _helper.get_user_and_chat(obj)
        if not (user and chat):
            return False

        admin = await chat.get_member(self._user_id or user.id)
        if admin.is_chat_creator() or admin.is_chat_admin():
            return True
        else:
            return False


class message:
    is_chat = f.ChatTypeFilter((t.ChatType.GROUP, t.ChatType.SUPERGROUP))
    is_private = f.ChatTypeFilter(t.ChatType.PRIVATE)
    is_reply = f.IsReplyFilter(True)


class bot:
    is_admin = AdminFilter(dp.bot.id)

    @staticmethod
    def has_permission(permissions: p.List[str]):
        permissions = set(permissions)

        async def filter(obj: objType):
            user, chat = _helper.get_user_and_chat(obj)
            admin = await chat.get_member(config.bot.id)
            _helper.has_permission(admin, permissions)

        return filter


class user:
    is_admin = AdminFilter()

    @staticmethod
    def has_permission(permissions: p.List[str]):
        permissions = set(permissions)

        async def filter(obj: objType):
            user, chat = _helper.get_user_and_chat(obj)
            admin = await chat.get_member(user.id)
            _helper.has_permission(admin, permissions)

        return filter
