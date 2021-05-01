from aiogram import types as t

token = ""
main_token = ""  # main bot token (-m --main)
test_token = ""  # test bot token (-t --test)

api_id = ""  # this can be found here https://my.telegram.org/apps
api_hash = ""  # this can be found here https://my.telegram.org/apps


# what languages does the bot support (specify in *language_code* format)
lang_encode = {
    "other": "English (Default)"  # {"en": "English", "ru": "Русский"}
}


bot: t.User  # this what *get_me* function return
