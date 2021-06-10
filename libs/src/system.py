import re

from aiogram.types.bot_command import BotCommand as C
from libs.classes import Button
from aiogram.dispatcher.filters.state import State, StatesGroup

back = Button("↩", "back")
delete_this = Button("🗑", "delete_this")

commands = [
    C("ban", "⛔ Block user"),
    C("unban", "✅ Unblock user"),
    C("kick", "⚠ Kick user"),
    C("mute", "🔇 Mute user"),
    C("unmute", "🔈 Unmute user"),
    C("purge", "🗑 Purge message"),
    C("settings", "⚙ Settings")
]

restrict_commands = ["ban", "unban", "kick", "mute", "unmute"]


class regex:
    class parse:
        command = r"(?P<command>^/(?P<command_text>[0-9a-zA-Z_]+)(?P<command_bot>@[0-9a-zA-Z_]+)?)"
        until = r"(?P<until>(?P<num>[1-9][0-9]*)(?P<type>[s|m|h|d|M|y]))"
        user = r"(?P<user>@[a-zA-Z][a-zA-Z0-9_]{4,})|(?P<id>[1-9][0-9]*)"
        reason = r"(?P<reason>[(|\"|\'](?P<raw_reason>.+)[)|\"|\'])"
        flags = r"(?P<flags>-[d|r]+)"
        all = re.compile(f"{command}|{until}|{user}|{reason}")

    class settings:
        chat_settings = r"^(?P<prefix>settings)@(?P<id>-100[0-9]+)$"
        alias_delete = r"^(?P<prefix>alias)@(?P<id>[0-9]+)$"
        data = r"^(?P<data>.+)@(?P<type>.+)$"


class states:
    class add_alias(StatesGroup):
        sticker = State()
        text = State()
        command = State()


if __name__ == "__main__":
    print(regex.parse.all.pattern)
