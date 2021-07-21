from libs.classes import CommandParser as p
from libs.classes import Commands as c
from libs.system import regex as r
from libs.system import restrict_commands
from aiogram.utils.markdown import hlink as l


class commands:

    class _help_text:
        users = f'👥 Упоминания (@username,{l("Вася Пупкин","t.me/username")} или ответ)'
        until = '⏳ Дата[s|m|h|d|M|y] (1m 30s или 1M)'
        reason = '❔ "Причина" (Да прям в кавычках)'
        poll = '📈 Сделать опрос (-p --poll)'

        ban = [users, until, reason, poll]
        unban = [users, reason, poll]
        kick = [users, reason, poll]
        mute = [users, until, reason, poll]
        unmute = [users, reason, poll]

        count = "🔢 Количество (2 - 1000)"
        reply = "⤴ Ответьте для удаления выше"

        purge = [count, reply]

    hide = c.Hide().add(
        c.Command("cancel", "◀️ Для выхода",
                  "Выходит из формы")
    )

    default_commands = c.Default().add(
        c.Command("fix", "🔧 Исправить подсказки для команд",
                  "Исправляет подсказки для команд"),
        c.Command("help", "🚑 Помощь по команам",
                  "Показывает справку (/help или /help ban)")
    )

    private_commands = c.Private().add(
        c.Command("settings", "⚙ Настройки", "Показывает настройки")
    )

    chat_commands = c.AllChat().add(

    )

    chat_admin_commands = c.AllAdmins().add(
        c.Command("ban", "⛔ Заблокировать пользователя", *_help_text.ban),
        c.Command("unban", "✅ Разблокировать пользователя", *_help_text.unban),
        c.Command("kick", "⚠ Исключить пользователя", *_help_text.kick),
        c.Command("mute", "🔇 Замутить пользователя", *_help_text.mute),
        c.Command("unmute", "🔈 Размутить пользователя", *_help_text.unmute),
        c.Command("purge", "🗑 Удалить сообщения", *_help_text.purge),
    )


class parsers:

    help = p.Command("help", "Команда справки").add(
        p.TextArg("Команда", "cmd", sep="")
    )

    restrict = p.Command(restrict_commands, "Админ команда").add(
        p.Arg(r.parse.reason, "reason", "Причина", False),
        p.DateArg("Срок"),
        p.UserArg("Пользователь"),
        p.FlagArg().add(
            p.Flag("p", "poll", "poll", "Флаг опроса")
        )
    )

    purge = p.Command("purge", "Команда очищения").add(
        p.NumberArg(2, 1000, "Количество сообщений", required=True)
    )

    test = p.Command("test", "Тест команда").add(
        p.NumberArg(2, 10, "Число вариантов", required=False)
    )


class poll:
    pass


command_list = c.Commands("ru").add(
    commands.hide,
    commands.default_commands,
    commands.private_commands,
    commands.chat_commands,
    commands.chat_admin_commands
)
