from libs.classes.CommandParser import Arg, BaseArg, Command, DateArg, UserArg
from libs.system import regex as r, restrict_commands
from aiogram.types import BotCommand as cmd, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators


command_list = {
    BotCommandScopeAllPrivateChats(): [
        cmd("settings", "⚙ Настройки")
    ],
    BotCommandScopeAllChatAdministrators(): [
        cmd("ban", "⛔ Заблокировать пользователя"),
        cmd("unban", "✅ Разблокировать пользователя"),
        cmd("kick", "⚠ Исключить пользователя"),
        cmd("mute", "🔇 Замутить пользователя"),
        cmd("unmute", "🔈 Размутить пользователя"),
        cmd("purge", "🗑 Удалить сообщения"),
    ]
}


class command:
    AdminCommandParser = Command(restrict_commands, "Админ команда").add(
        Arg(r.parse.reason, "reason", "Причина", False),
        DateArg("Срок"),
        UserArg("Пользователь")
    )
