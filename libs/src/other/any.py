from libs.classes.CommandParser import Arg, BaseArg, Command, DateArg, UserArg
from libs.system import regex as r, restrict_commands


class command:
    AdminCommandParser = Command(restrict_commands, "Admin command").add(
        Arg(r.parse.reason, "reason", "Reason", False),
        DateArg("Date"),
        UserArg("User")
    )
