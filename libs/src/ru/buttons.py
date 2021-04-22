from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from libs.classes import Button, Menu, MenuButton


class chat:
    class admin:
        undo = Button("↩ Отмена", "undo").inline


class private:
    class settings:
        alias = Button("Сокращение для стикера", "alias")

        settings = Menu("Выберете что хотите настроить").add(
            MenuButton(
                "Админ команды",
                "Выберете что хотите настроить"
            ).add(
                alias
            )
        )
