from libs import stages as s
from src.commands import alias_commands, set_report_commands
from locales import text as t


class add_alias(s.StageGroup):
    sticker = s.Stage(text=t.private.settings.alias_sticker)
    text = s.Stage(text=t.private.settings.alias_text)
    command = s.Stage(alias_commands, text=t.private.settings.alias_command)


class set_report_command(s.StageGroup):
    command = s.Stage(set_report_commands, text=t.private.settings.report_command)


class set_report_count(s.StageGroup, text=t.private.settings.report_count):
    count = s.Stage(text=t.private.settings.report_count)


class set_report_delta(s.StageGroup):
    delta = s.Stage(text=t.private.settings.report_delta)
