from aiogram.types import BotCommand as cmd
from aiogram.types import (BotCommandScopeAllChatAdministrators,
                           BotCommandScopeAllGroupChats,
                           BotCommandScopeAllPrivateChats)
from libs.classes.CommandParser import (Arg, BaseArg, Command, DateArg,
                                        NumberArg, TextArg, UserArg)
from libs.system import regex as r
from libs.system import restrict_commands

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
    PurgeParser = Command("purge", "Команда очищения").add(
        NumberArg(2, 100, "Количество", required=True)
    )
