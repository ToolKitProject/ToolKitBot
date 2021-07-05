from libs.classes.CommandParser import Arg, BaseArg, Command, DateArg, UserArg
from libs.system import regex as r, restrict_commands
from aiogram.types import BotCommand as cmd, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators, BotCommandScopeDefault


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
        UserArg("User")
    )
