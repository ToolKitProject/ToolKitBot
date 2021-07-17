import typing as p
import re
from asyncio import sleep
from random import randint

from aiogram import types as t

from bot import bot, dp
from libs import filters as f
from libs import system
from libs.src.other.any import command as c
from libs.classes.Buttons import Menu
from libs.classes.Chat import Chat
from libs.classes.Errors import BackError, MyError, ERRORS, IGNORE, ForceError
from libs.classes.Localisation import UserText
from libs.objects import Database, MessageData


async def test_clb(clb: t.CallbackQuery):  # Test func
    await clb.answer(dp.callback_query_handlers.handlers.__len__())


async def check(msg: t.Message):
    """
    Creates records in the database
    """
    if await f.message.is_chat.check(msg) and not Database.get_chat(msg.chat.id):
        await Chat.create(msg.chat)
    if not Database.get_user(msg.from_user.id):
        Database.add_user(msg.from_user.id)

    return False


# @dp.callback_query_handler(test_clb)
# @any.command.AdminCommandParser()
# @dp.edited_message_handler(commands=["test"])
# @dp.message_handler(commands=["test"])
@c.TestParser()
async def test_xd(msg: t.Message):  # Test func
    src = UserText(msg.from_user.language_code)
    parsed = await src.any.command.TestParser.parse(msg)

    count = parsed.number if parsed.number else 10

    correct = randint(0, count - 1)
    options = [str(i + 1) for i in range(count)]
    await msg.answer_poll(
        "Угадай правильный",
        options,
        is_anonymous=False,
        type=t.PollType.QUIZ,
        correct_option_id=correct,
        explanation=f"Правильный ответ {correct + 1}"
    )


@dp.message_handler(f.message.is_private, commands=["start"])
async def start(msg: t.Message):
    """
    Start command handler
    """
    src = UserText(msg.from_user.language_code)
    await msg.answer(src.text.private.start_text)


@system.delete_this(state="*")
async def delete_this(clb: t.CallbackQuery):
    """
    delete_this button handler
    """
    await MessageData.delete(clb.message, False)


@system.back()
async def back(clb: t.CallbackQuery):
    """
    back button handler
    """
    msg = clb.message
    with await MessageData.data(msg) as data:
        try:
            history: p.List[Menu] = data.history
            history.pop(-1)
            await history[-1].edit(msg, False)
            data.history = history
        except Exception:
            raise BackError(clb.from_user.language_code)


@dp.my_chat_member_handler(f.user.add_member)
async def bot_chat_added(upd: t.ChatMemberUpdated):
    """
    If bot added in the chat
    """
    chat: Chat = await Chat.create(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.start_text)


@dp.my_chat_member_handler(f.user.removed_member)
async def bot_chat_removed(upd: t.ChatMemberUpdated):
    """
    If bot removed in the chat
    """
    Database.delete_chat(upd.chat.id)


@dp.my_chat_member_handler(f.user.promote_admin)
async def bot_promote(upd: t.ChatMemberUpdated):
    """
    If bot promote to admin
    """
    chat: Chat = await Chat.create(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.promote_admin)


@dp.my_chat_member_handler(f.user.restrict_admin)
async def bot_chat_restrict(upd: t.ChatMemberUpdated):
    """
    If bot restrict to admin
    """
    chat: Chat = await Chat.create(upd.chat)
    src = chat.owner.src
    await bot.send_message(chat.id, src.text.chat.restrict_admin)


@dp.message_handler(f.message.is_chat, f.message.is_alias,
                    content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_executor(msg: t.Message):
    """
    Execute the alias as a new update
    """
    upd = t.Update.get_current()  # Get update obj
    chat = await Chat.create(msg.chat)  # Get chat obj
    text = None

    # Edit text
    if msg.sticker:
        aliases = chat.settings.sticker_alias
        msg.sticker = None
    elif msg.text:
        aliases = chat.settings.text_alias

    for als, txt in aliases.items():
        pattern = re.compile(f"^{als}", re.IGNORECASE)
        if pattern.match(msg.text):
            text = pattern.sub(txt, msg.text)
    msg.text = text

    # Process update
    upd.message = msg
    await dp.process_update(upd)


@dp.message_handler(check, content_types=[t.ContentType.TEXT, t.ContentType.PHOTO])
async def check():
    """
    Execute check func
    """
    pass


@dp.errors_handler()
async def errors(upd: t.Update, error: p.Union[MyError, Exception]):
    """
    Errors handler
    """
    if error.__class__ in ERRORS:  # If my errors
        await error.answer()
    elif error.__class__ in IGNORE:  # If errors must be ignored
        return True
    else:  # Other errors
        my_err = ForceError(f"⚠ {error.__class__.__name__}:{error.args[0]}", 0, True, False)
        await my_err.log()
        if upd.message and await f.message.is_private.check(upd.message):  # if private chat
            await my_err.answer()

    return True
