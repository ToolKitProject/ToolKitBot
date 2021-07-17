from xmlrpc.client import TRANSPORT_ERROR
from aiogram.types import BotCommand as cmd
from aiogram.types import (BotCommandScopeAllChatAdministrators,
                           BotCommandScopeAllGroupChats,
                           BotCommandScopeAllPrivateChats)
from libs.classes.CommandParser import (
    Arg, BaseArg, Command, DateArg, Flag, FlagArg,
    NumberArg, TextArg, UserArg
)
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
        UserArg("Пользователь"),
        FlagArg().add(
            Flag("p", "poll", "poll", "Флаг опроса")
        )
    )

    PurgeParser = Command("purge", "Команда очищения").add(
        NumberArg(2, 1000, "Количество сообщений", required=True)
    )

    TestParser = Command("test", "Тест команда").add(
        NumberArg(2, 10, "Число вариантов", required=False)
    )


class poll:
    pass
