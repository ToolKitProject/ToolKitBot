import typing as p
from datetime import timedelta

from aiogram import types as t

from bot import bot, client
from libs.classes import Database as d
from libs.objects import Database
from .Chat import Chat
from .Database import permissionOBJ, settingsOBJ
from .Localisation import UserText


class User:  # TODO:Добавить коментарии
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

    settings: settingsOBJ
    permission: permissionOBJ
    owns: p.List[d.chatOBJ]

    MUTE = t.ChatPermissions(can_send_messages=False)
    UNMUTE = t.ChatPermissions(*[True] * 8)

    @classmethod
    async def create(cls, auth: p.Union[str, int, t.User]):
        """

        @rtype: User
        """
        cls = User()

        if isinstance(auth, t.User):
            cls._user = auth
        else:
            cls._user = await client.get_users(auth)
        cls.user = Database.get_user(cls._user.id)
        if not cls.user:
            cls.user = Database.add_user(cls._user.id)

        cls.id = cls._user.id
        cls.username = cls._user.username
        cls.first_name = cls._user.first_name
        cls.last_name = cls._user.last_name
        cls.language_code = cls._user.language_code
        cls.lang = cls.language_code
        cls.src = UserText(cls.lang)

        cls.settings = cls.user.settings
        cls.permission = cls.user.permission
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
            return self.username
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

    async def send(self,
                   text: str,
                   parse_mode: p.Optional[str] = None,
                   entities: p.Optional[p.List[t.MessageEntity]] = None,
                   disable_web_page_preview: p.Optional[bool] = None,
                   disable_notification: p.Optional[bool] = None,
                   reply_to_message_id: p.Optional[int] = None,
                   allow_sending_without_reply: p.Optional[bool] = None,
                   reply_markup: p.Union[t.InlineKeyboardMarkup,
                                         t.ReplyKeyboardMarkup,
                                         t.ReplyKeyboardRemove,
                                         t.ForceReply, None] = None,
                   ):
        await bot.send_message(self.id,
                               text=text,
                               entities=entities,
                               parse_mode=parse_mode,
                               disable_web_page_preview=disable_web_page_preview,
                               disable_notification=disable_notification,
                               reply_to_message_id=reply_to_message_id,
                               allow_sending_without_reply=allow_sending_without_reply,
                               reply_markup=reply_markup, )

    async def get_owns(self) -> p.List[Chat]:
        return [await Chat.create(c.id) for c in self.owns]

    async def ban(self, chat_id: int, until: timedelta):
        await bot.ban_chat_member(chat_id, self.id, until_date=until)

    async def unban(self, chat_id: int):
        await bot.unban_chat_member(chat_id, self.id, only_if_banned=True)

    async def mute(self, chat_id: int, until: timedelta):
        await bot.restrict_chat_member(chat_id, self.id, self.MUTE, until_date=until)

    async def unmute(self, chat_id: int):
        await bot.restrict_chat_member(chat_id, self.id, self.UNMUTE)

    async def kick(self, chat_id: int):
        await bot.unban_chat_member(chat_id, self.id, only_if_banned=False)
