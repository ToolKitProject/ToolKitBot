from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes.Buttons import Button, Menu, MenuButton
from libs.classes.Settings import DictSettings, Elements, Settings


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo")

        check_poll = Button("✅ Проверить опрос", "check_poll")
        cancel_poll = Button("⛔ Отменить опрос", "cancel_poll")

        poll = IM(row_width=1).add(
            check_poll.button,
            cancel_poll.button
        )


class private:
    class settings:
        class chat:
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

            chats = Menu("Выбери чат", True)

            delete = Menu("Удалить ?", undo=False)
            delete_yes = Button("Да 🗑", "delete_yes")
            delete_no = Button("Нет ↩", "back")
            delete.add(
                delete_yes,
                delete_no
            )

        class private:
            change_lang = Button("Изменить язык", "change_lang")
            private_settings = Settings("Выбери что хочешь настроить", "Себя", "private_settings").add(
                change_lang
            )

        chat_settings = Button("Чаты", "chat_list")
        private_settings = Button(private.private_settings.text,
                                  private.private_settings.key)
        settings = Menu("Выбери что хочешь настроить", row=2).add(
            # private_settings,
            chat_settings
        )
