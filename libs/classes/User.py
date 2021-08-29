import typing as p
from datetime import timedelta

from aiogram import types as t, Bot
from aiogram.utils.exceptions import MigrateToChat, ChatNotFound

from libs.classes import Database as d
from libs.objects import Database
from .Chat import Chat
from .Database import permissionOBJ, settingsOBJ, reportsOBJ, userOBJ
from libs import UserText
from . import Errors as e


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
    settings: settingsOBJ
    permission: permissionOBJ
    reports: reportsOBJ
    owns: p.List[d.chatOBJ]

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
        self.reports = self.userOBJ.reports
        self.owns = Database.get_owns(self.id)

    @classmethod
    async def create(cls, auth: p.Union[str, int, t.User, None] = None):
        """

        @rtype: User
        """
        from bot import client

        if isinstance(auth, t.User):
            user = auth
        elif auth:
            user = await client.get_users(auth)
        else:
            user = t.User.get_current(True)

        return cls(user)

    @property
    def full_name(self):
        result = self.first_name
        if self.last_name:
            result += f" {self.last_name}"
        return result

    @property
    def mention(self):
        if self.username:
            return f"@{self.username}"
        else:
            return self.full_name

    @property
    def link(self):
        return f"<a href='tg://user?id={self.id}'>{self.full_name}</a>"

    @property
    def ping(self):
        if self.username:
            return f"@{self.username}"
        else:
            return self.link

    @property
    def global_reports(self):
        result = 0
        for r in self.reports.values():
            result += r
        return result

    @property
    def statistic_mode(self):
        s = self.settings["statistic"]
        if s:
            return s["mode"] if "mode" in s else 2
        else:
            return 2

    async def get_owns(self) -> p.List[Chat]:
        owns = []
        for chat in self.owns:
            try:
                owns.append(await Chat.create(chat.id))
            except (MigrateToChat, ChatNotFound):
                Database.delete_chat(chat.id)
            except Exception as ex:
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
