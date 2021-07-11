import typing as p

from aiogram import types as t, filters as f

import config
from bot import dp
from libs.classes import Utils as u
from libs.classes.Chat import Chat

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
    def has_permission(admin: t.ChatMember, permissions: p.Set[str]):
        if t.ChatMemberStatus.is_chat_creator(admin.status):
            return True
        elif t.ChatMemberStatus.is_chat_admin(admin.status):
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
        chat = await Chat.create(msg.chat)

        if msg.sticker:
            alias = list(chat.settings.sticker_alias.keys())
            text = msg.sticker.file_unique_id
        elif msg.text:
            alias = list(chat.settings.text_alias.keys())
            text = msg.text

        return text in alias


class message:
    is_chat = f.ChatTypeFilter((t.ChatType.GROUP, t.ChatType.SUPERGROUP))
    is_private = f.ChatTypeFilter(t.ChatType.PRIVATE)
    is_reply = f.IsReplyFilter(True)
    is_alias = AliasFilter()


class bot:
    is_admin = AdminFilter(dp.bot.id)

    @staticmethod
    def has_permission(permissions: p.List[str]):
        permissions = list(set(permissions))

        async def filter(obj: objType):
            user, chat = _helper.get_user_and_chat(obj)
            admin = await chat.get_member(config.bot.id)
            return _helper.has_permission(admin, permissions)

        return filter


class user:
    is_admin = AdminFilter()

    @staticmethod
    def has_permission(permissions: p.List[str]):
        permissions = set(permissions)

        async def filter(obj: objType):
            user, chat = _helper.get_user_and_chat(obj)
            admin = await chat.get_member(user.id)
            return _helper.has_permission(admin, permissions)

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
