import typing as p
from datetime import timedelta

from aiogram import types as t, Bot

from src.instances import Database, Cache
from libs.database import chatOBJ
from src.utils import get_value


class Chat:
    chat: t.Chat
    chatOBJ: chatOBJ

    id: int
    type: str
    title: str
    username: str
    invite_link: str
    settings: p.Dict

    def __init__(self, chat: t.Chat, owner: t.User):
        self.chat = chat
        self.owner = owner
        self.chatOBJ = Database.get_chat(chat.id, self.owner.id)

        self.id = chat.id
        self.type = chat.type
        self.title = chat.title
        self.username = chat.username
        self.invite_link = chat.invite_link

        self.settings = self.chatOBJ.settings

        if self.chatOBJ.owner_id != self.owner.id:
            self.chatOBJ.owner_id = self.owner.id

    @classmethod
    @Cache.register(timedelta(minutes=10))
    async def create(cls, auth: p.Union[int, str, t.Chat]) -> "Chat":
        from libs.user import User
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

        try:
            await chat.export_invite_link()
        except Exception:
            pass

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
    def statistic_mode(self) -> int:
        return get_value(self.settings, ["statistic", "mode"], default=1)

    @property
    def report_command(self) -> str:
        return get_value(self.settings, ["report", "command"], default="/ban")

    @property
    def report_count(self) -> int:
        return get_value(self.settings, ["report", "count"], default=3)

    @property
    def report_delta(self) -> timedelta:
        return timedelta(seconds=get_value(
            self.settings,
            ["report", "delta"],
            default=timedelta(days=365).total_seconds()
        ))
