from aiogram import types as t
import typing as p
import gettext as g
import os


class Text(str):
    message: str
    added: p.List["Text"]

    def __init__(self, message: str):
        self.message = message
        self.added = []

    def __str__(self):
        return self.text

    def __repr__(self):
        return repr(self.message)

    def __iter__(self):
        return iter(self.text)

    def __getitem__(self, item: int):
        return self.text[item]

    def __add__(self, other: p.Union["Text"]):
        self.added.append(other)
        return self

    @property
    def text(self):
        src = UserText()
        added = "".join([a.text for a in self.added])
        return src(self.message) + added


class UserText:
    lang: str
    translation: g.NullTranslations

    def __init__(self):
        user = t.User.get_current()
        if user:
            self.lang = user.language_code
        else:
            self.lang = "other"

        _l = [self.lang]
        if self.lang not in os.listdir("libs/locales"):
            _l = None

        self.translation = g.translation("ToolKit", "libs/locales", languages=_l)
        self.translation.install()

        from libs import src
        self.text = src.text
        self.buttons = src.buttons
        self.any = src.any

    def __call__(self, message: str) -> str:
        return self.translation.gettext(message)
