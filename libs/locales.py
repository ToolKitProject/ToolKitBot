from collections import UserString

from aiogram import types as t
import typing as p
import gettext as g
import os

lang = None


# noinspection PyMissingConstructor
class Text(UserString):
    message: str
    _added: p.List[p.Union["Text", str]]

    def __init__(self, message: str):
        self.message = message
        self._added = []

    def __add__(self, other: p.Union["Text"]):
        self._added.append(other)
        return self

    @property
    def added(self) -> str:
        text = ""
        for a in self._added:
            text += str(a)
        return text

    @property
    def data(self):
        src = UserText()
        return src(self.message) + self.added


class UserText:
    lang: str
    gettext: p.Callable[[str], str]

    def __init__(self):
        from libs.objects import Database
        user = t.User.get_current()

        self.lang = None
        if user:  # if user found
            self.lang = user.language_code

            userOBJ = Database.get_user(user.id)
            if userOBJ.settings.lang:  # if user setup his lang
                self.lang = userOBJ.settings.lang
        else:
            self.lang = lang

        if self.lang not in os.listdir("libs/locales"):
            self.lang = None

        if self.lang:
            tn = g.translation("ToolKit", "libs/locales", languages=[self.lang])
            self.gettext = tn.gettext
        else:
            self.gettext = g.gettext

        from libs import src
        self.text = src.text
        self.buttons = src.buttons
        self.any = src.any

    def __call__(self, message: str) -> str:
        return self.gettext(message)
