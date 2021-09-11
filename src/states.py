from libs import stages as s
from src.commands import alias_commands


class add_alias(s.StageGroup):
    sticker = s.Stage()
    text = s.Stage()
    command = s.Stage(alias_commands)


class set_report_command(s.StageGroup):
    command = s.Stage(alias_commands)


class set_report_count(s.StageGroup):
    count = s.Stage()


class set_report_delta(s.StageGroup):
    delta = s.Stage()
