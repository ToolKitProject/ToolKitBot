from aiogram import types as t
from aiogram.dispatcher.middlewares import BaseMiddleware

import typing as p
from src import other, filters as f
from src.objects import Database
from libs.database import LogType as l
from aiogram.types import ContentType as c


async def get_help(msg: t.Message):
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


def get_value(_dict: p.Dict, key_history: p.List, default: p.Any = None):
    for k in key_history:
        if k in _dict:
            _dict = _dict[k]
        else:
            return default
    return _dict


class NewInstance(BaseMiddleware):
    def __init__(self):
        self.chek_types = [
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

            if msg.content_type in self.chek_types and await f.message.is_chat.check(msg):
                chat = await Chat.create(msg.chat)
                user = await User.create(msg.from_user)

                mode = chat.statistic_mode
                if user.statistic_mode < mode:
                    mode = user.statistic_mode

                if mode == 2:
                    Database.add_message(msg.from_user.id, msg.chat.id, msg.message_id, msg.text, msg.content_type,
                                         msg.date)
                elif mode == 1:
                    Database.add_message(msg.from_user.id, msg.chat.id, msg.message_id, type=msg.content_type,
                                         date=msg.date)
                elif mode == 0:
                    Database.add_message(msg.from_user.id, msg.chat.id, msg.message_id)


class LogMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_update(self, upd: t.Update, *args):
        upd = upd.chat_member
        if upd:
            member = upd.new_chat_member.user
            date = upd.date.isoformat(" ")

            txt = None
            if f.user.promote_admin(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.PROMOTE_ADMIN, date)
            if f.user.restrict_admin(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.RESTRICT_ADMIN, date)

            if f.user.promote_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.PROMOTE_MEMBER, date)
            if f.user.restrict_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.RESTRICT_MEMBER, date)

            if f.user.add_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.ADD_MEMBER, date)
            if f.user.removed_member(upd):
                Database.add_log(upd.chat.id, upd.from_user.id, member.id, l.REMOVE_MEMBER, date)
