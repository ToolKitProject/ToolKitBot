from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton, Settings, DictSettings, Element


class chat:
    class admin:
        undo = Button("↩ Undo", "undo")


class private:
    class settings:
        settings = Settings("Test", "Text button", "settings")

        settings.add(
            DictSettings("Dick", "Text", "dick_settings").add(
                Element("Button", "element")
            )
        )
