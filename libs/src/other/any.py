from aiogram.types import BotCommand as cmd
from aiogram.types import (BotCommandScopeAllChatAdministrators,
                           BotCommandScopeAllGroupChats,
                           BotCommandScopeAllPrivateChats,
                           BotCommandScopeDefault)
from libs.classes.CommandParser import (
    Arg, BaseArg, Command, DateArg, Flag, FlagArg,
    NumberArg, TextArg, UserArg
)
from libs.system import regex as r
from libs.system import restrict_commands

command_list = {
    BotCommandScopeAllPrivateChats(): [
        cmd("settings", "⚙ Settings")
    ],
    BotCommandScopeAllChatAdministrators(): [
        cmd("ban", "⛔ Block user"),
        cmd("unban", "✅ Unblock user"),
        cmd("kick", "⚠ Kick user"),
        cmd("mute", "🔇 Mute user"),
        cmd("unmute", "🔈 Unmute user"),
        cmd("purge", "🗑 Purge message"),
    ]
}


class command:
    AdminCommandParser = Command(restrict_commands, "Admin command").add(
        Arg(r.parse.reason, "reason", "Reason", False),
        DateArg("Date"),
        UserArg("User"),
        FlagArg().add(
            Flag("p", "poll", "poll", "Poll flag")
        )
    )

    PurgeParser = Command("purge", "Purge command").add(
        NumberArg(2, 1000, "Message count", required=True)
    )

    TestParser = Command("test", "Тест команда").add(
        NumberArg(2, 10, "Count options", required=False)
    )


class poll:
    pass
