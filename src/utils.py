import typing as p
from copy import copy

from aiogram import types as t
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ContentType as c

from bot import bot
from libs.database import LogType as l
from . import filters as f
from .instances import Database


async def get_help(msg: t.Message):
    from locales import other

    if await f.message.is_reply.check(msg):
        return True
    if not msg.get_args():
        await msg.reply(other.command_list.get(msg.get_command(True).removeprefix("/")),
                        disable_web_page_preview=True)
        return False
    return True


async def write_action(msg: t.Message):
    if isinstance(msg, t.CallbackQuery):
        msg = msg.message
    await msg.answer_chat_action(t.ChatActions.TYPING)
    return True


def get_value(_dict: dict, key_history: list, default: p.Any = None) -> p.Any:
    result = default

    for key in key_history:
        if isinstance(_dict, dict) and key in _dict:
            _dict = _dict[key]
            result = _dict
        else:
            return default

    return result


def save_target_settings(target):
    from libs.chat import Chat
    from libs.user import User

    if isinstance(target, User):
        target.userOBJ.settings = target.settings
    elif isinstance(target, Chat):
        target.chatOBJ.settings = target.settings


def get_aliases(msg: t.Message) -> dict:
    user_settings = Database.get_user(msg.from_user.id).settings
    chat_settings = Database.get_chat(msg.chat.id).settings

    aliases = {}
    if msg.sticker:
        aliases.update(get_value(chat_settings, ["sticker_alias"], {}))
        aliases.update(get_value(user_settings, ["sticker_alias"], {}))
    elif msg.text:
        aliases.update(get_value(chat_settings, ["text_alias"], {}))
        aliases.update(get_value(user_settings, ["text_alias"], {}))

    return aliases


def get_alias_text(msg: t.Message) -> str:
    if msg.text:
        return msg.text
    elif msg.sticker:
        return msg.sticker.file_unique_id


def get_key_by_id(_dict: dict, id: int) -> p.Any:
    return list(_dict.keys())[int(id)]


def break_list_by_step(_list: list, step: int) -> list[list]:
    result = []

    for i in range((len(_list) // step) + 1):
        result.append(_list[i * step:i * step + step])

    return result


async def raise_permissions_errors(users: list[t.User], admins: list[t.ChatMember]):
    from libs import errors as e
    from libs.user import User

    users: list[User]
    err = None

    for u1 in copy(users):
        for u2 in copy(users):
            if u1 is u2:
                continue
            if u1.id == u2.id:
                users.remove(u1)

    for user in copy(users):
        for admin in admins:
            if user.id == bot.id:
                err = e.CantRestrictSelf(user.ping)
            elif admin.user.id == user.id:
                if admin.status == t.ChatMemberStatus.OWNER:
                    err = e.CantRestrictChatOwner(user.ping)
                else:
                    err = e.UserIsAnAdministratorOfTheChat(user.ping)

        if err is not None:
            await err.answer()
            users.remove(user)
            err = None


class NewInstance(BaseMiddleware):
    def __init__(self):
        self.check_types = [
            c.ANIMATION,
            c.AUDIO,
            c.CONTACT,
            c.DICE,
            c.DOCUMENT,
            c.GAME,
            c.LOCATION,
            c.PHOTO,
            c.POLL,
            c.STICKER,
            c.TEXT,
            c.VENUE,
            c.VIDEO,
            c.VIDEO_NOTE,
            c.VOICE
        ]
        super().__init__()

    async def on_process_update(self, upd: t.Update, *args):
        from libs.chat import Chat
        from libs.user import User

        msg = upd.message
        if msg:
            if await f.message.is_chat.check(msg) and not Database.get_chat(msg.chat.id):
                await Chat.create(msg.chat)
            Database.get_user(msg.from_user.id)

            if msg.content_type in self.check_types and await f.message.is_chat.check(msg):
                chat = await Chat.create(msg.chat)
                user = await User.create(msg.from_user)

                mode = chat.statistic_mode
                if user.statistic_mode < mode:
                    mode = user.statistic_mode

                user_id = msg.from_user.id
                chat_id = msg.chat.id
                message_id = msg.message_id
                reply_message_id = msg.reply_to_message.message_id if msg.reply_to_message else None
                text = msg.text
                type = msg.content_type
                date = msg.date

                if mode <= 0:
                    text = None

                Database.add_message(
                    user_id=user_id,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_message_id=reply_message_id,
                    message=text,
                    type=type,
                    date=date,
                )


class LogMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_update(self, upd: t.Update, *args):
        upd = upd.chat_member
        if upd:
            member = upd.new_chat_member.user

            if f.user.promote_admin(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.PROMOTE_ADMIN, upd.date)
            if f.user.restrict_admin(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.RESTRICT_ADMIN, upd.date)

            if f.user.promote_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.PROMOTE_MEMBER, upd.date)
            if f.user.restrict_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.RESTRICT_MEMBER, upd.date)

            if f.user.add_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.ADD_MEMBER, upd.date)
            if f.user.removed_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.REMOVE_MEMBER, upd.date)
