import asyncio

from libs import UserText
from aiogram.utils import exceptions as ex
from aiogram import types as t
from asyncio import sleep
import logging
from traceback import format_exc


class MyError(Exception):
    def __init__(self, auto_delete: int = 0, delete: bool = True, alert: bool = True):
        self.src = UserText()
        self.auto_delete = auto_delete
        self.delete = delete
        self.alert = alert

        self.text = None

    @property
    def args(self):
        return list(self.__dict__.values())

    @staticmethod
    def get_text(upd: t.Update) -> str:
        if upd.message:
            return upd.message.text
        elif upd.callback_query:
            return upd.callback_query.data

    @staticmethod
    def get_user(upd: t.Update) -> t.User:
        if upd.message:
            return upd.message.from_user
        elif upd.callback_query:
            return upd.callback_query.from_user
        elif upd.chat_member or upd.my_chat_member:
            member = upd.chat_member or upd.my_chat_member
            return member.from_user

    async def answer(self):
        from libs.src.buttons import delete_this
        upd = t.Update.get_current()
        rm = None
        if self.delete:
            rm = delete_this.menu
        if upd.edited_message:
            upd.message = upd.edited_message

        if upd.message:
            msg = await upd.message.answer(self.text, reply_markup=rm)
            if self.auto_delete:
                try:
                    await sleep(self.auto_delete)
                    await msg.delete()
                except Exception:
                    pass
        elif upd.callback_query:
            await upd.callback_query.answer(self.text, self.alert, cache_time=int(self.auto_delete))
        else:
            pass

    async def log(self):
        upd = t.Update.get_current()
        error = f"{format_exc()}" + \
                f"User: {self.get_user(upd).mention}\n" + \
                f"Message: {self.get_text(upd)} \n"
        logging.error(error)

    def __str__(self):
        return self.text


class ForceError(MyError):
    def __init__(self, text: str, auto_delete: int = 0, delete: bool = True, alert: bool = True):
        self.text = text
        self.auto_delete = auto_delete
        self.delete = delete
        self.alert = alert


class CommandNotFound(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.CommandNotFound
        self.auto_delete = False
        self.delete = False
        self.alert = False


class UserNotFound(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.UserNotFound
        self.auto_delete = 5
        self.delete = True
        self.alert = True


class ArgumentError(MyError):
    def __init__(self):
        super().__init__()
        self.text = f"{self.src.text.errors.argument_error.ArgumentError}"
        self.auto_delete = 0
        self.delete = True
        self.alert = True

    class ArgumentRequired(MyError):
        def __init__(self, arg_name: str):
            super().__init__()
            self.arg_name = arg_name
            self.context = self.src.text.errors.argument_error.required
            self.text = f"{self.src.text.errors.argument_error.ArgumentError}\n" \
                        f"┗━{self.context.format(**self.__dict__)}"
            self.auto_delete = 0
            self.delete = True
            self.alert = True

    class ArgumentIncorrect(MyError):
        def __init__(self, arg_name: str):
            super().__init__()
            self.arg_name = arg_name
            self.context = self.src.text.errors.argument_error.incorrect
            self.text = f"{self.src.text.errors.argument_error.ArgumentError}\n" \
                        f"┗━{self.context.format(**self.__dict__)}"
            self.auto_delete = 0
            self.delete = True
            self.alert = True


class HasNotPermission(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.HasNotPermission
        self.auto_delete = 0
        self.delete = True
        self.alert = True


class EmptyOwns(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.EmptyOwns
        self.auto_delete = 5
        self.delete = True
        self.alert = True


class AliasTypeError(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.alias_type_error.AliasTypeError
        self.auto_delete = 5
        self.delete = True
        self.alert = True

    class AliasCommandNotSupported(MyError):
        def __init__(self):
            super().__init__()
            self.text = f"{self.src.text.errors.alias_type_error.AliasTypeError}\n" \
                        f"┗━{self.src.text.errors.alias_type_error.command_not_supported}"
            self.auto_delete = False
            self.delete = False
            self.alert = False

    class AliasStickerSupported(MyError):
        def __init__(self):
            super().__init__()
            self.text = f"{self.src.text.errors.alias_type_error.AliasTypeError}\n" \
                        f"┗━{self.src.text.errors.alias_type_error.sticker_supported}"
            self.auto_delete = False
            self.delete = False
            self.alert = False

    class AliasTextSupported(MyError):
        def __init__(self):
            super().__init__()
            self.text = f"{self.src.text.errors.alias_type_error.AliasTypeError}\n" \
                        f"┗━{self.src.text.errors.alias_type_error.text_supported}"
            self.auto_delete = False
            self.delete = False
            self.alert = False


class AlreadyExists(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.AlreadyExists
        self.auto_delete = 5
        self.delete = True
        self.alert = True


class NotReply(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.NotReply
        self.auto_delete = 5
        self.delete = True
        self.alert = True


class BotHasNotPermission(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.BotHasNotPermission
        self.auto_delete = 0
        self.delete = True
        self.alert = True


class BackError(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.BackError
        self.auto_delete = 5
        self.delete = True
        self.alert = True


class PollCheck(MyError):
    def __init__(self):
        super().__init__()
        self.text = self.src.text.errors.PollCheck
        self.auto_delete = 5
        self.delete = True
        self.alert = True


ERRORS = [
    ForceError,
    CommandNotFound,
    UserNotFound,
    ArgumentError.ArgumentRequired,
    ArgumentError.ArgumentIncorrect,
    ArgumentError,
    HasNotPermission,
    EmptyOwns,
    AliasTypeError,
    AliasTypeError.AliasStickerSupported,
    AliasTypeError.AliasTextSupported,
    AliasTypeError.AliasCommandNotSupported,
    AlreadyExists,
    NotReply,
    BotHasNotPermission,
    BackError,
    PollCheck
]

IGNORE = [
    ex.MessageNotModified,
    ex.Throttled,
    ex.TimeoutWarning,
    ex.NetworkError,
    asyncio.TimeoutError,
]
