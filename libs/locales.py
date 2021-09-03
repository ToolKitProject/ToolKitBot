import json
from collections import UserString
from copy import deepcopy

from aiogram import types as t
import typing as p
import gettext as g
import os

lang = None


class TextEncoder(json.JSONEncoder):
    def default(self, object):
        if isinstance(object, Text):
            result = str(object)
        else:
            result = super().default(object)
        return result


# noinspection PyMissingConstructor
class Text(UserString):
    messages: p.List[str]
    _format_callback: p.Callable[[str], str]

    def __init__(self, message: str):
        self.messages = [message]
        self._format_callback = None

    def __add__(self, other: p.Union["Text"]) -> "Text":
        new = deepcopy(self)
        new.messages.append(other)
        return new

    @property
    def data(self):
        src = UserText()
        message = ""

        for msg in self.messages:
            txt = src(msg)
            if self._format_callback:
                txt = self._format_callback(txt)
            message += txt

        return message

    def format_callback(self):
        def wrapper(func):
            self._format_callback = func
            return func

        return wrapper


class UserText:
    lang: str
    gettext: p.Callable[[str], str]

    def __init__(self):
        from src.objects import Database
        from src.utils import get_value

        user = t.User.get_current()

        self.lang = None
        if user:  # if user found
            userOBJ = Database.get_user(user.id)
            self.lang = get_value(userOBJ.settings, "lang", user.language_code)
        else:
            self.lang = lang

        if self.lang not in os.listdir("locales"):
            self.lang = None

        if self.lang:
            tn = g.translation("ToolKit", "locales", languages=[self.lang])
            self.gettext = tn.gettext
        else:
            self.gettext = g.gettext

    def __call__(self, message: str) -> str:
        return self.gettext(message)
