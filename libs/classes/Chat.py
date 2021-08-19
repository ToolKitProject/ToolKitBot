import typing as p

from aiogram import types as t, Bot

from libs.objects import Database
from .Database import chatOBJ, settingsOBJ


class Chat:
    _chat: t.Chat
    chatOBJ: chatOBJ

    id: int
    type: str
    title: str
    username: str
    invite_link: str
    settings: settingsOBJ

    @classmethod
    async def create(cls, auth: p.Union[int, str, t.Chat, None] = None):
        """

        @rtype: Chat
        """
        bot = Bot.get_current()
        cls = Chat()

        if isinstance(auth, t.Chat):
            cls._chat = auth
        elif auth:
            cls._chat = await bot.get_chat(auth)
        else:
            cls._chat = t.Chat.get_current(True)

        if cls._chat.type in [t.ChatType.PRIVATE]:
            ValueError("Chat type incorrect")

        cls.owner = await cls._owner()
        cls.chatOBJ = Database.get_chat(cls._chat.id, cls.owner.id)

        cls.id = cls._chat.id
        cls.type = cls._chat.type
        cls.title = cls._chat.title
        cls.username = cls._chat.username
        cls.invite_link = None

        cls.settings = cls.chatOBJ.settings

        if cls.chatOBJ.owner.id != cls.owner.id:
            cls.chatOBJ.owner = cls.owner.id

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

    @property
    def statistic_mode(self):
        s = self.settings["statistic"]
        return s["mode"] if "mode" in s else 2

    async def _owner(self):
        from .User import User
        admins = await self._chat.get_administrators()
        for admin in admins:
            if t.ChatMemberStatus.is_chat_creator(admin.status):
                result = await User.create(admin.user)
                return result
