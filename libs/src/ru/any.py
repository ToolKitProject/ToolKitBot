from libs.classes.CommandParser import Arg, BaseArg, Command, DateArg, UserArg
from libs.system import regex as r, restrict_commands


class command:
    AdminCommandParser = Command(restrict_commands, "Админ команда").add(
        Arg(r.parse.reason, "reason", "Причина", False),
        DateArg("Срок"),
        UserArg("Пользователь")
    )
