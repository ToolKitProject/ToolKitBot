from aiogram import types

token = ""
main_token = ""  # main bot token (-m --main)
test_token = ""  # test bot token (-t --test)

api_id = ""  # this can be found here https://my.telegram.org/apps
api_hash = ""  # this can be found here https://my.telegram.org/apps

# what languages does the bot support (specify in *language_code* format)
lang_support = []  # libs.src.{lang} (*other* if lang not support)

# Decoding language_code
lang_encode = {
    "other": "English (Default)"  # {"en": "English", "ru": "Русский"}
}


bot: types.User  # this what *get_me* function return
