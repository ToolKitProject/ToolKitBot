from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton


class chat:
    class admin:
        undo = Button("↩ Undo", "undo")


class private:
    class settings:
        settings = Menu("Choose what you want customize")

        chats = Button("Chats", "chats")  # to chats_menu
        chats_menu = Menu("Choose a chat")

        chat_settings = Menu("Choose option")
        sticker_alias = MenuButton("Manage a sticker aliases", "Choose action")
        command_alias = MenuButton("Manage a command aliases", "Choose action")

        add_alias = Button("Add alias", "add_alias")
        edit_alias = Button("Ha it's a template", "edit_alias")

        # private_settings = MenuButton("Youself", "private_settings") #TODO

        # ?____compile
        settings.add(
            chats
        )
        chat_settings.add(
            sticker_alias.add(
                add_alias
            ),
            command_alias.add(
                add_alias
            )
        )
