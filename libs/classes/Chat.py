import typing as p

from aiogram import types as t, Bot

from libs.objects import Database
from .Database import chatOBJ, settingsOBJ


class Chat:
    chat: t.Chat
    chatOBJ: chatOBJ

    id: int
    type: str
    title: str
    username: str
    invite_link: str
    settings: settingsOBJ

    def __init__(self, chat: t.Chat):
        self.chat = chat
        self.owner = await self._owner()
        self.chatOBJ = Database.get_chat(chat.id, self.owner.id)

        self.id = chat.id
        self.type = chat.type
        self.title = chat.title
        self.username = chat.username
        self.invite_link = None

        self.settings = self.chatOBJ.settings

        if self.chatOBJ.owner.id != self.owner.id:
            self.chatOBJ.owner = self.owner.id

    @classmethod
    async def create(cls, auth: p.Union[int, str, t.Chat, None] = None) -> "Chat":
        bot = Bot.get_current()
        if isinstance(auth, t.Chat):
            chat = auth
        elif auth:
            chat = await bot.get_chat(auth)
        else:
            chat = t.Chat.get_current(True)

        if chat.type in [t.ChatType.PRIVATE]:
            raise ValueError("Chat type incorrect")

        return cls(chat)

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
        if s:
            return s["mode"] if "mode" in s else 2
        else:
            return 2

    async def _owner(self):
        from .User import User
        admins = await self.chat.get_administrators()
        for admin in admins:
            if admin.status == t.ChatMemberStatus.CREATOR:
                result = await User.create(admin.user)
                return result
