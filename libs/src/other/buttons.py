from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes.Buttons import Button, Menu, MenuButton
from libs.classes.Settings import DictSettings, Elements, Settings


class chat:
    class admin:
        undo = Button("↩ Undo", "undo")

        check_poll = Button("✅ Check poll", "check_poll")
        cancel_poll = Button("⛔ Cancel poll", "cancel_poll")

        poll = IM(row_width=1).add(
            check_poll.button,
            cancel_poll.button
        )


class private:
    class settings:
        class chat:
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

            chats = Menu("Choose chat", True)

            delete = Menu("Delete ?", undo=False)
            delete_yes = Button("Yes 🗑", "delete_yes")
            delete_no = Button("No ↩", "back")
            delete.add(
                delete_yes,
                delete_no
            )

        class private:
            change_lang = Button("Change language", "change_lang")
            private_settings = Settings("Choose what you want to customize", "Self", "private_settings").add(
                change_lang
            )

        chat_settings = Button("Chats", "chat_list")
        private_settings = Button(private.private_settings.text,
                                  private.private_settings.key)
        settings = Menu("Choose what you want to customize", row=2).add(
            # private_settings,
            chat_settings
        )
