import typing as p
from datetime import timedelta

from aiogram import types as t, Bot

from libs.objects import Database, Cache
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

    def __init__(self, chat: t.Chat, owner: t.User):
        self.chat = chat
        self.owner = owner
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
    @Cache.register(timedelta(minutes=10), 10)
    async def create(cls, auth: p.Union[int, str, t.Chat]) -> "Chat":
        from .User import User
        bot = Bot.get_current()
        if isinstance(auth, t.Chat):
            chat = auth
        else:
            chat = await bot.get_chat(auth)

        if chat.type in [t.ChatType.PRIVATE]:
            raise ValueError("Chat type incorrect")

        owner = None
        for admin in await chat.get_administrators():
            if admin.status == t.ChatMemberStatus.CREATOR:
                owner = await User.create(admin.user)

        return cls(chat, owner)

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
