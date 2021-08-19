import typing as p
from datetime import timedelta

from aiogram import types as t

from bot import dp
from libs import filters as f
from libs.classes.Chat import Chat
from libs.classes.CommandParser import ParsedArgs
from libs.classes.Errors import MyError, ERRORS, IGNORE, ForceError
from libs.classes.User import User
from libs.objects import Database
from libs.src import any

chek_types = t.ContentType.all()
chek_types.remove(t.ContentType.NEW_CHAT_MEMBERS)
chek_types.remove(t.ContentType.LEFT_CHAT_MEMBER)
chek_types.remove(t.ContentType.INVOICE)
chek_types.remove(t.ContentType.SUCCESSFUL_PAYMENT)
chek_types.remove(t.ContentType.CONNECTED_WEBSITE)
chek_types.remove(t.ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED)
chek_types.remove(t.ContentType.MIGRATE_TO_CHAT_ID)
chek_types.remove(t.ContentType.MIGRATE_FROM_CHAT_ID)
chek_types.remove(t.ContentType.PINNED_MESSAGE)
chek_types.remove(t.ContentType.NEW_CHAT_TITLE)
chek_types.remove(t.ContentType.NEW_CHAT_PHOTO)
chek_types.remove(t.ContentType.DELETE_CHAT_PHOTO)
chek_types.remove(t.ContentType.GROUP_CHAT_CREATED)
chek_types.remove(t.ContentType.PASSPORT_DATA)
chek_types.remove(t.ContentType.PROXIMITY_ALERT_TRIGGERED)
chek_types.remove(t.ContentType.VOICE_CHAT_SCHEDULED)
chek_types.remove(t.ContentType.VOICE_CHAT_STARTED)
chek_types.remove(t.ContentType.VOICE_CHAT_ENDED)
chek_types.remove(t.ContentType.VOICE_CHAT_PARTICIPANTS_INVITED)


async def check(msg: t.Message):
    """
    Creates records in the database
    """

    if msg.content_type not in chek_types:
        return False

    if await f.message.is_chat.check(msg):
        chat = await Chat.create()
    user = await User.create()

    if await f.message.is_chat.check(msg):
        mode = chat.statistic_mode
        if user.statistic_mode < mode:
            mode = user.statistic_mode

        if mode == 2:
            Database.add_message(msg.from_user.id, msg.chat.id, msg.text, msg.content_type, msg.date)
        elif mode == 1:
            Database.add_message(msg.from_user.id, msg.chat.id, None, msg.content_type, msg.date)

    return False


@dp.errors_handler()
async def errors(_, error: p.Union[MyError, Exception]):
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
        await my_err.answer()

    return True


@dp.message_handler(check, content_types=t.ContentType.ANY)
async def check():
    """
    Execute check func
    """
    pass


# @dp.message_handler(commands=["test"])
@any.parsers.test()
async def test_xd(msg: t.Message, parsed: ParsedArgs):  # Test func

    member = await msg.chat.get_member(msg.from_user.id)
    if member.status != t.ChatMemberStatus.OWNER:
        return

    delta: timedelta = parsed.delta
    from_date = msg.date - delta
    to_date = msg.date

    messagesOBJ = Database.get_messages_by_date(from_date, to_date)
    if messagesOBJ:
        text = f"Сообщения за {delta}\n"
        for messageOBJ in messagesOBJ:
            text += "========\n"
            if messageOBJ.message:
                text += f"{messageOBJ.message} \n\n{messageOBJ.type}  |  {messageOBJ.date}\n"
            else:
                text += f"{messageOBJ.type}  |  {messageOBJ.date}\n"
        text += "========"

        await msg.answer(text)
    else:
        await msg.answer("Сообщений нет")
