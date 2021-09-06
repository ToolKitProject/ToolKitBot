from aiogram import types as t

from bot import bot
from libs import errors as e
from libs.command_parser import ParsedArgs
from libs.user import User
from src.instances import MessageData
from src import filters as f
from locales import buttons as b
from .restrict import get_text, execute_action


@b.chat.admin.check_poll(
    f.message.is_chat,
    f.user.has_permission("can_restrict_members")
)
async def check_poll(clb: t.CallbackQuery):
    poll = clb.message.poll
    executor = await User.create(clb.from_user)
    if poll.total_voter_count < 2:
        raise e.PollCheck()

    yes = poll.options[0]
    no = poll.options[1]

    if yes.voter_count > no.voter_count:
        with MessageData.data() as data:
            parsed: ParsedArgs = data.parsed
            if await execute_action(parsed, clb.message.chat.id):
                text, rm = await get_text(parsed, executor)  # Get text
                to_msg = await clb.message.reply(text, reply_markup=rm)  # Send text
                await MessageData.move(clb.message, to_msg)
    else:
        await MessageData.delete(clb.message, True)

    await bot.stop_poll(clb.message.chat.id, clb.message.message_id)


@b.chat.admin.cancel_poll(
    f.message.is_chat,
    f.user.has_permission("can_restrict_members")
)
async def cancel_poll(clb: t.CallbackQuery):
    await MessageData.delete(clb.message, True)
    await bot.stop_poll(clb.message.chat.id, clb.message.message_id)
