from aiogram import types as t
from aiogram.dispatcher.middlewares import BaseMiddleware

import typing as p
from libs import filters as f
from libs import UserText
from .objects import Database
from aiogram.types import ContentType as c


async def get_help(msg: t.Message):
    src = UserText()
    if await f.message.is_reply.check(msg):
        return True
    if not msg.get_args():
        await msg.reply(src.any.command_list.get(msg.get_command(True).removeprefix("/")),
                        disable_web_page_preview=True)
        return False
    return True


async def write_action(msg: t.Message):
    if isinstance(msg, t.CallbackQuery):
        msg = msg.message
    await msg.answer_chat_action(t.ChatActions.TYPING)
    return True


class UpdateDatabase(BaseMiddleware):
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

    async def on_process_update(self, upd: t.Update, date: p.Dict):
        from libs.classes.Chat import Chat
        from libs.classes.User import User

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
