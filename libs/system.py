from aiogram.dispatcher.filters.state import State, StatesGroup

from libs.classes.Buttons import Button

back = Button("↩", "back")
delete_this = Button("🗑", "delete_this")


def info(text: str):
    return Button("❓", f"info@{text}")


restrict_commands = ["ban", "unban", "kick", "mute", "unmute"]

alias_commands = [*restrict_commands, "purge"]


class regex:
    class parse:
        command = r"(?P<full>^/(?P<text>[0-9a-zA-Z_]+)(?P<bot>@[0-9a-zA-Z_]+)?)"
        date = r"(?P<date>(?P<num>[1-9][0-9]*)(?P<type>[s|m|h|d|w|M|y]))"
        user = r"(?P<user>@[a-zA-Z][a-zA-Z0-9_]{4,})"
        reason = r"(?P<full>[(|\"|\'](?P<raw>.+)[)|\"|\'])"

        text = r"(?P<text>\w[\w ]*$)"
        number = r"(?P<number>-?[\d]+)"

        flag = r"(?P<flag>(?P<prefix>—|--|-)(?P<text>\w+))"
        value_flag = r""

    class settings:
        chat_settings = r"^(?P<prefix>settings)@(?P<id>-100[0-9]+)$"
        alias_delete = r"^(?P<prefix>alias)@(?P<id>[0-9]+)$"
        data = r"^(?P<data>.+)@(?P<type>.+)$"


class states:
    class add_alias(StatesGroup):
        sticker = State()
        text = State()
        command = State()
