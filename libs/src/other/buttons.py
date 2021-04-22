from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton


class chat:
    class admin:
        undo = Button("↩ Undo", "undo").inline


class private:
    class settings:
        alias = Button("Alias for sticker", "alias")

        settings = Menu("Choose what you want to customize").add(
            MenuButton(
                "Admin commands",
                "Choose what you want to customize"
            ).add(
                alias
            )
        )
