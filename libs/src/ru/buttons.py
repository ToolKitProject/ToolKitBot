from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo")


class private:
    class settings:
        settings = Menu("Выбери что хочешь настроить", row=2, undo=False)
        chats = Button("Чаты", "chats_menu")

        chats_menu = Menu("Выбери чат")

        chat_settings = Menu("Выбери что хочешь настроить", row=2)
        sticker_alias = Button(
            "Сокращения к стикерам",
            "alias_menu@sticker_alias"
        )
        command_alias = Button(
            "Сокращения к командам",
            "alias_menu@command_alias"
        )

        alias_menu = Menu("Выбери действие")
        add_alias = Button("Добавить сокращение", "add_alias")

        # private_settings = MenuButton("Себя", "private_settings")  # TODO

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
