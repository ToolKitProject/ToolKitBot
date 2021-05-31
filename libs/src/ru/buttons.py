from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import (Button, DictSettings, Elements, Menu, MenuButton,
                          Settings)


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo")


class private:
    class settings:
        add_alias = Button("Добавить сокращение", "add_sticker_alias")

        chat_settings = Settings("Выбери что хочешь настроить", "Имя чата", "chat_settings", row=2).add(
            DictSettings("Нажми, чтобы удалить", "Сокращения по стикерам", "sticker_alias").add(
                add_alias,
                Elements("{value}", "{key}")
            ),
            DictSettings("Нажми, чтобы удалить", "Сокращения по тексту", "text_alias").add(
                add_alias,
                Elements("{key} ➡ {value}", "{num}")
            )
        )

        chat_list = Button("Чаты", "chat_list")
        settings = Menu("Выбери что хочешь настроить").add(
            chat_list
        )

        chats = Menu("Выбери чат", True)
