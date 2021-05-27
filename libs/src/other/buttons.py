from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton, Settings, DictSettings, Elements

test = Menu("Test").add(
    MenuButton("Test menu", "Test menu", "test_menu").add(
        Button("Test", "test_btn")
    ),
    MenuButton("Test menu 2", "Test menu 2", "test_menu2").add(
        Button("Тест2", "test_btn2")
    )
)


class chat:
    class admin:
        undo = Button("↩ Undo", "undo")


class private:
    class settings:
        add_alias = Button("Add alias", "add_alias")

        chat_settings = Settings("Choose what you want to customize", "Имя чата", "chat_settings", row=2).add(
            DictSettings("Click to delete", "Alias for sticker", "sticker_alias").add(
                add_alias,
                Elements("{value}", "{key}")
            ),
            DictSettings("Click to delete", "Alias for text", "text_alias").add(
                add_alias,
                Elements("{key} ➡ {value}", "{num}")
            )
        )

        chat_list = Button("Chats", "chat_list")
        settings = Menu("Choose what you want to customize").add(
            chat_list
        )

        chats = Menu("Choose chat", True)
