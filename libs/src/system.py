import re
from libs.classes import Button
from aiogram.dispatcher.filters.state import State, StatesGroup

back = Button("↩", "back")


class regex:
    class parse:
        cmd = r"(?P<cmd>^/(?P<action>[0-9a-zA-Z_]+)(?P<bot>@[0-9a-zA-Z_]+)?)"
        until = r"(?P<until>(?P<num>[1-9][0-9]*)(?P<type>[s|m|h|d|M|y]))"
        user = r"(?P<user>@[a-zA-Z][a-zA-Z0-9_]{4,})|(?P<id>[1-9][0-9]*)"
        reason = r"(?P<reason>[(|\"|\'](?P<raw_reason>.+)[)|\"|\'])"
        all = re.compile(f"{cmd}|{until}|{user}|{reason}")

    class settings:
        chat_settings = r"^(?P<prefix>settings)@(?P<id>-100[0-9]+)$"
        alias_delete = r"^(?P<prefix>alias)@(?P<id>[0-9]+)$"
        data = r"^(?P<data>.+)@(?P<type>.+)$"


class states:
    class add_alias(StatesGroup):
        alias = State()
        command = State()


if __name__ == "__main__":
    print(regex.parse.all.pattern)
