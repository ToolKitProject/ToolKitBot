from datetime import timedelta

from aiogram import types as t, Bot

from libs import errors as e, database as d
from libs.database import userOBJ, LogType as l
from libs.locales import UserText
from src.instances import Cache
from src.instances import Database
from src.utils import get_value


class User:
    """
    Пользователь
    """
    user: t.User
    id: int
    username: str
    first_name: str
    last_name: str
    language_code: str
    lang: str
    src: UserText

    userOBJ: userOBJ
    settings: dict
    permission: dict

    MUTE = t.ChatPermissions(can_send_messages=False)
    UNMUTE = t.ChatPermissions(*[True] * 8)

    def __init__(self, user: t.User):
        self.user = user
        self.userOBJ = Database.get_user(user.id)

        self.id = user.id
        self.username = user.username
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.language_code = user.language_code
        self.lang = self.language_code
        self.src = UserText()

        self.settings = self.userOBJ.settings
        self.permission = self.userOBJ.permission

    @classmethod
    @Cache.register(timedelta(minutes=10))
    async def create(cls, auth: str | int | t.User) -> "User":
        from bot import client

        if isinstance(auth, t.User):
            user = auth
        else:
            user = await client.get_users(auth)

        return cls(user)

    @property
    def full_name(self) -> str:
        result = self.first_name
        if self.last_name:
            result += f" {self.last_name}"
        return result

    @property
    def mention(self) -> str:
        if self.username:
            return f"@{self.username}"
        else:
            return self.full_name

    @property
    def link(self) -> str:
        return f"<a href='tg://user?id={self.id}'>{self.full_name}</a>"

    @property
    def ping(self) -> str:
        if self.username:
            return f"@{self.username}"
        else:
            return self.link

    @property
    def statistic_mode(self) -> int:
        return get_value(self.settings, ["statistic", "mode"], 1)

    @property
    def owns(self) -> list[d.chatOBJ]:
        return Database.get_chats(owner_id=self.id)

    async def get_owns(self):
        from libs.chat import Chat

        owns: list[Chat] = []
        for chat in self.owns:
            try:
                owns.append(await Chat.create(chat.id))
            except Exception as ex:
                Database.delete_chat(chat.id)
                await e.ForceError(f"⚠ {ex.args[0]}").answer()

        return owns

    async def ban(self, chat_id: int, until: timedelta):
        bot = Bot.get_current()
        await bot.ban_chat_member(chat_id, self.id, until_date=until)

    async def unban(self, chat_id: int):
        bot = Bot.get_current()
        await bot.unban_chat_member(chat_id, self.id, only_if_banned=True)

    async def mute(self, chat_id: int, until: timedelta):
        bot = Bot.get_current()
        await bot.restrict_chat_member(chat_id, self.id, self.MUTE, until_date=until)

    async def unmute(self, chat_id: int):
        bot = Bot.get_current()
        await bot.restrict_chat_member(chat_id, self.id, self.UNMUTE)

    async def kick(self, chat_id: int):
        bot = Bot.get_current()
        await bot.unban_chat_member(chat_id, self.id, only_if_banned=False)

    def get_reports(self, chat: t.Chat):
        from libs.chat import Chat
        chat: Chat

        return len(Database.get_logs(
            chat_id=chat.id,
            target_id=self.id,
            type=l.REPORT,
            delta=chat.report_delta
        ))
