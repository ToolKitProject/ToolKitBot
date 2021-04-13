from aiogram.types import InlineKeyboardMarkup as IM
from aiogram.types import InlineKeyboardButton as IB


class chat:
    class admin:
        undo = IM().add(
            IB("↩ Undo", callback_data="undo")
        )
