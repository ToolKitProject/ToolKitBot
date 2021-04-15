from .Localisation import UserText as usr


class CommandNotFound(Exception):
    def __init__(self, lang) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.CommandNotFound)

    def __str__(self):
        return self.args[0]


class UserNotFound(Exception):
    def __init__(self, lang) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.UserNotFound)

    def __str__(self):
        return self.args[0]


class ArgumentError(Exception):
    def __init__(self, lang) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.ArgumentError)

    def __str__(self):
        return self.args[0]


class HasNotPermission(Exception):
    def __init__(self, lang) -> None:
        usrc = usr(lang)
        super().__init__(usrc.text.errors.HasNotPermission)

    def __str__(self):
        return self.args[0]


ERRORS = [
    CommandNotFound,
    UserNotFound,
    ArgumentError,
    HasNotPermission
]

IGNORE = [

]
