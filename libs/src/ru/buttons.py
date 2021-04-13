from aiogram.types import InlineKeyboardMarkup as IM
from aiogram.types import InlineKeyboardButton as IB


class chat:
    class admin:
        undo = IM().add(
            IB("↩ Отмена", callback_data="undo")
        )
