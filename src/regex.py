def alias(alias: str):
    return f"^{alias}( |$)"


class parse:
    command = r"(?P<full>^/(?P<text>[0-9a-zA-Z_]+)(?P<bot>@[0-9a-zA-Z_]+)?)"
    date = r"(?P<date>(?P<num>[1-9][0-9]*)(?P<type>[s|m|h|d|w|M|y]))"
    user = r"(?P<user>@[a-zA-Z][a-zA-Z0-9_]{4,})"
    reason = r"(?P<full>[(|\"|\'](?P<raw>.+?)[)|\"|\'])"

    text = r"(?P<text>\w+)"
    number = r"(?P<number>-?[\d]+)"

    flag = r"(?P<flag>(?P<prefix>—|--|-)(?P<text>[\w-]+))(\s|$)"
    value_flag = r"(?P<flag>(?P<prefix>—|--|-)(?P<text>[\w-]+)[:|=](?P<value>[\"|'].+?[\"|']|\w+))(\s|$)"


class settings:
    chat_settings = r"^(?P<prefix>settings)@(?P<id>-100[0-9]+)$"
    alias_delete = r"^(?P<prefix>alias)@(?P<id>[0-9]+)$"
    data = r"^(?P<data>.+)@(?P<type>.+)$"
