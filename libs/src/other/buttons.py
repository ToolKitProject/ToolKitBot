from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton


class chat:
    class admin:
        undo = Button("↩ Undo", "undo")


class private:
    class settings:
        settings = Menu("Choose what you want customize", row=2, undo=False)
        chats = Button("Chats", "chats_menu")

        chats_menu = Menu("Choose a chat")  # Вывод кнопок

        chat_settings = Menu("Choose option", row=2)  # При выборе чата
        sticker_alias = Button(
            "Manage a sticker aliases",
            "alias_menu@sticker_alias"
        )
        command_alias = Button(
            "Manage a command aliases",
            "alias_menu@command_alias"
        )

        alias_menu = Menu("Choose action")  # При выборе типа настройки
        add_alias = Button("Add alias", "add_alias")

        # private_settings = MenuButton("Youself", "private_settings") #TODO

        # ?____compile
        settings.add(
            chats
        )
        chat_settings.add(
            sticker_alias,
            command_alias
        )
        alias_menu.add(
            add_alias
        )
