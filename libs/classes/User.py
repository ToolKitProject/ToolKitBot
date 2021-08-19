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
    _user: t.User
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

    @classmethod
    async def create(cls, auth: p.Union[str, int, t.User, None] = None):
        """

        @rtype: User
        """
        from bot import client
        cls = User()

        if isinstance(auth, t.User):
            cls._user = auth
        elif auth:
            cls._user = await client.get_users(auth)
        else:
            cls._user = t.User.get_current(True)

        cls.userOBJ = Database.get_user(cls._user.id)

        cls.id = cls._user.id
        cls.username = cls._user.username
        cls.first_name = cls._user.first_name
        cls.last_name = cls._user.last_name
        cls.language_code = cls._user.language_code
        cls.lang = cls.language_code
        cls.src = UserText()

        cls.settings = cls.userOBJ.settings
        cls.permission = cls.userOBJ.permission
        cls.reports = cls.userOBJ.reports
        cls.owns = Database.get_owns(cls.id)

        return cls

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
        return s["mode"] if "mode" in s else 2

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
