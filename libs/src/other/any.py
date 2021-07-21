from libs.classes import CommandParser as p
from libs.classes import Commands as c
from libs.system import regex as r
from libs.system import restrict_commands
from aiogram.utils.markdown import hlink as l


class commands:
    class _help_text:
        users = f'👥 Mentions (@username,{l(f"Jack Jackson", "t.me/username")} or reply)'
        until = '⏳ Date[s|m|h|d|M|y] (1m 30s or 1M)'
        reason = '❔ "Reason" (Yes in the quote)'
        poll = '📈 Make a poll (-p --poll)'

        ban = [users, until, reason, poll]
        unban = [users, reason, poll]
        kick = [users, reason, poll]
        mute = [users, until, reason, poll]
        unmute = [users, reason, poll]

        count = "🔢 Count (2 - 1000)"
        reply = "⤴ Reply to delete above"

        purge = [count, reply]

    hide = c.Hide().add(
        c.Command("cancel", "◀️ To cancel",
                  "Exit from form")
    )

    default_commands = c.Default().add(
        c.Command("fix", "🔧 Fix hints for commands",
                  "Fixes hints for commands"),
        c.Command("help", "🚑 Help for commands",
                  "Shows help (/help or /help ban)")
    )

    private_commands = c.Private().add(
        c.Command("settings", "⚙ Settings", "Shows settings")
    )

    chat_commands = c.AllChat().add(

    )

    chat_admin_commands = c.AllAdmins().add(
        c.Command("ban", "⛔ Block user", *_help_text.ban),
        c.Command("unban", "✅ Unblock user", *_help_text.unban),
        c.Command("kick", "⚠ Kick user", *_help_text.kick),
        c.Command("mute", "🔇 Mute user", *_help_text.mute),
        c.Command("unmute", "🔈 Unmute user", *_help_text.unmute),
        c.Command("purge", "🗑 Purge messages", *_help_text.purge),
    )


class parsers:
    help = p.Command("help", "Help command").add(
        p.TextArg("Command", "cmd", sep="")
    )

    restrict = p.Command(restrict_commands, "Admin command").add(
        p.Arg(r.parse.reason, "reason", "Reason", False),
        p.DateArg("Date"),
        p.UserArg("User"),
        p.FlagArg().add(
            p.Flag("p", "poll", "poll", "Poll flag")
        )
    )

    purge = p.Command("purge", "Purge command").add(
        p.NumberArg(2, 1000, "Message count", required=True)
    )

    test = p.Command("test", "Тест команда").add(
        p.NumberArg(2, 10, "Count options", required=False)
    )


class poll:
    pass


command_list = c.Commands("other").add(
    commands.hide,
    commands.default_commands,
    commands.private_commands,
    commands.chat_commands,
    commands.chat_admin_commands
)
