from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo")


class private:
    class settings:
        settings = Menu("Выбери что хочешь настроить")

        chats = Button("Чаты", "chats")
        chats_menu = Menu("Выбери чат")

        chat_settings = Menu("Выбери что хочешь настроить")
        sticker_alias = MenuButton("Сокращения к стикерам", "Выбери действие")
        command_alias = MenuButton("Сокращения к командам", "Выбери действие")

        add_alias = Button("Добавить сокращение", "add_alias")
        edit_alias = Button("Ха это шаблон", "edit_alias")

        # private_settings = MenuButton("Себя", "private_settings")  # TODO

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
