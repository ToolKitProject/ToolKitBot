from aiogram import types as t

from handlers.chat.admin.restrict import process_restrict, command_text
from libs.command_parser import ParsedArgs
from libs.user import User
from locales import buttons
from src import filters as f
from libs import errors as e
from src.instances import MessageData


@buttons.chat.admin.check_poll(
    f.message.is_chat,
    f.user.has_permission("can_restrict_members")
)
async def check_poll_now(clb: t.CallbackQuery):
    poll = clb.message.poll
    executor = await User.create(clb.from_user)
    parsed: ParsedArgs = MessageData.data().parsed

    if poll.total_voter_count < 2:
        raise e.PollCheck()

    yes = poll.options[0].voter_count
    no = poll.options[1].voter_count

    if yes > no:
        await process_restrict(parsed)
        txt, rm = command_text(parsed, executor)
        to_msg = await clb.message.reply(txt, reply_markup=rm)
        await MessageData.move(clb.message, to_msg)
    else:
        await MessageData.delete(clb.message)
