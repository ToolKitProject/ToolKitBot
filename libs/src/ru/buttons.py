from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, DictSettings, Elements, Menu, MenuButton, Settings

test = Menu("Тест").add(
    MenuButton("Тест меню", "Тест меню", "test_menu").add(
        Button("Тест", "test_btn")
    ),
    MenuButton("Тест меню 2", "Тест меню 2", "test_menu2").add(
        Button("Тест2", "test_btn2")
    )
)


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo")


class private:
    class settings:
        add_alias = Button("Добавить сокращение", "add_alias")

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
