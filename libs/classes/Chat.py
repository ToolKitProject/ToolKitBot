from typing import *

from aiogram import types as t

from bot import bot
from libs.objects import Database
from .Database import chatOBJ, settingsOBJ


class Chat:
    _chat: t.Chat
    chat: chatOBJ

    id: int
    type: str
    title: str
    username: str
    invite_link: str
    settings: settingsOBJ

    @classmethod
    async def create(cls, auth: Union[int, str, t.Chat]):
        """

        @rtype: Chat
        """
        cls = Chat()

        if isinstance(auth, t.Chat):
            cls._chat = auth
        elif auth:
            cls._chat = await bot.get_chat(auth)
        else:
            cls._chat = t.Chat.get_current(True)

        cls.chat = Database.get_chat(cls._chat.id)
        if not cls.chat:
            cls.chat = Database.add_chat(cls._chat.id, (await cls._owner()).id)

        if cls._chat.type not in [t.ChatType.GROUP, t.ChatType.SUPERGROUP]:
            ValueError("Чет не так")

        cls.id = cls._chat.id
        cls.type = cls._chat.type
        cls.title = cls._chat.title
        cls.username = cls._chat.username
        cls.invite_link = None
        # cls.invite_link = await cls._chat.get_url()

        cls.settings = cls.chat.settings
        cls.owner = await cls._owner()

        if cls.chat.owner.id != cls.owner.id:
            cls.chat.id = cls.owner.id

        return cls

    @property
    def mention(self):
        if self.username:
            return self.username
        else:
            return self.title

    @property
    def link(self):
        return f"<a href='{self.invite_link}'>{self.title}</a>"

    @property
    def ping(self):
        if self.username:
            return f"@{self.username}"
        else:
            return self.link

    async def _owner(self):
        from .User import User
        admins = await self._chat.get_administrators()
        for admin in admins:
            if t.ChatMemberStatus.is_chat_creator(admin.status):
                result = await User.create(admin.user)
                return result
