import typing as p

from aiogram import types as t

from bot import bot, dp
from libs import filters as f
from libs import system
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
        await Database.add_user(msg.from_user.id)

    return False


# @dp.callback_query_handler(test_clb)
# @any.command.AdminCommandParser()
@dp.message_handler(commands=["test"])
async def test_xd(msg: t.Message):  # Test func
    await msg.answer(msg.reply_to_message.message_id)


@dp.message_handler(f.message.is_private, commands=["start"])
async def start(msg: t.Message):
    """
    Start command handler
    """
    src = UserText(msg.from_user.language_code)
    await msg.answer(src.text.private.start_text)


@system.delete_this(f.message.is_chat, state="*")
async def delete_this(clb: t.CallbackQuery):
    """
    delete_this button handler
    """
    await clb.message.delete()


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


@dp.message_handler(f.message.is_chat, f.message.is_alias, f.message.is_reply,
                    content_types=[t.ContentType.TEXT, t.ContentType.STICKER])
async def alias_executor(msg: t.Message):
    """
    Execute the alias as a new update
    """
    upd = t.Update.get_current()  # Get update obj
    chat = await Chat.create(msg.chat)  # Get chat obj

    # Edit update text
    if msg.sticker:
        msg.text = chat.settings.sticker_alias[msg.sticker.file_unique_id]
        msg.sticker = None
    elif msg.text:
        msg.text = chat.settings.text_alias[msg.text]
    else:
        return

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
@dp.async_task
async def errors(upd: t.Update, error: p.Union[MyError, Exception]):
    """
    Errors handler
    """
    if error.__class__ in ERRORS:
        await error.answer(upd)
    elif error.__class__ in IGNORE:
        pass
    else:
        my_err = ForceError(f"⚠ {error.__class__.__name__}:{error.args[0]}", 0, True, False)
        await my_err.log(upd)
        if upd.message and t.ChatType.is_group_or_super_group(upd.message.chat):
            return
        await my_err.answer(upd)

    return True
