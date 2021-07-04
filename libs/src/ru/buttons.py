from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes.Buttons import Button, Menu, MenuButton
from libs.classes.Settings import DictSettings, Elements, Settings


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo")


class private:
    class settings:
        add_alias = Button("Добавить сокращение", "add_sticker_alias")

        chat_settings = Settings("Выбери что хочешь настроить", "Имя чата", "chat_settings", row=2).add(
            DictSettings("Нажми, чтобы удалить", "Сокращения по стикерам", "sticker_alias").add(
                add_alias,
                Elements("{value}", "alias:{key}")
            ),
            DictSettings("Нажми, чтобы удалить", "Сокращения по тексту", "text_alias").add(
                add_alias,
                Elements("{key} ➡ {value}", "alias:{key}")
            )
        )

        chat_list = Button("Чаты", "chat_list")
        settings = Menu("Выбери что хочешь настроить").add(
            chat_list
        )

        chats = Menu("Выбери чат", True)

        delete = Menu("Удалить ?", undo=False)
        delete_yes = Button("Да 🗑", "delete_yes")
        delete_no = Button("Нет ↩", "back")
        delete.add(
            delete_yes,
            delete_no
        )
