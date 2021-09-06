import os

# (./locales)
langs = {
    "ru": "🇷🇺 Русский",
    # "pl": "🇵🇱 Polski"
}
assert \
    len(langs) == len(os.listdir("locales")), \
    "Add lang to dict plz )))"

restrict_commands = ["ban", "unban", "kick", "mute", "unmute"]
clear_commands = ["clear_history", "purge"]
alias_commands = [*restrict_commands, *clear_commands]
_cancel = ["cancel"]
