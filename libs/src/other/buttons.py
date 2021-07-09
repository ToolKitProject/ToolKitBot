from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes.Buttons import Button, Menu, MenuButton
from libs.classes.Settings import DictSettings, Elements, Settings


class chat:
    class admin:
        undo = Button("↩ Undo", "undo")


class private:
    class settings:
        add_alias = Button("Add alias", "add_sticker_alias")

        chat_settings = Settings("Choose what you want to customize", "Имя чата", "chat_settings", row=2).add(
            DictSettings("Click to delete", "Alias for sticker", "sticker_alias").add(
                add_alias,
                Elements("{value}", "alias:{key}")
            ),
            DictSettings("Click to delete", "Alias for text", "text_alias").add(
                add_alias,
                Elements("{key} ➡ {value}", "alias:{key}")
            )
        )

        chat_list = Button("Chats", "chat_list")
        settings = Menu("Choose what you want to customize").add(
            chat_list
        )

        chats = Menu("Choose chat", True)

        delete = Menu("Delete ?", undo=False)
        delete_yes = Button("Yes 🗑", "delete_yes")
        delete_no = Button("No ↩", "back")
        delete.add(
            delete_yes,
            delete_no
        )
