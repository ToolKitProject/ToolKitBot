from .Localisation import UserText as usr
from aiogram.utils import exceptions as ex


class CommandNotFound(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.CommandNotFound, *args)

    def __str__(self):
        return self.args[0]


class UserNotFound(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.UserNotFound, *args)

    def __str__(self):
        return self.args[0]


class ArgumentError(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.ArgumentError, *args)

    def __str__(self):
        return self.args[0]


class HasNotPermission(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.HasNotPermission, *args)

    def __str__(self):
        return self.args[0]


class EmptyOwns(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.EmptyOwns, *args)

    def __str__(self):
        return self.args[0]


class TypeError(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.TypeError, *args)

    def __str__(self):
        return self.args[0]


class AlreadyExists(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.AlreadyExists, *args)

    def __str__(self):
        return self.args[0]


class NotReply(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.NotReply, *args)

    def __str__(self):
        return self.args[0]


class BotHasNotPermission(Exception):
    def __init__(self, lang, *args) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.BotHasNotPermission, *args)

    def __str__(self):
        return self.args[0]


ERRORS = [
    CommandNotFound,
    UserNotFound,
    ArgumentError,
    HasNotPermission,
    EmptyOwns,
    TypeError,
    AlreadyExists,
    NotReply,
    BotHasNotPermission
]

IGNORE = [
    ex.MessageNotModified
]
