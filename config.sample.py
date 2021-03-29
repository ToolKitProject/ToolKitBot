from aiogram import types

token = ""
main_token = ""  # main bot token (-m --main)
test_token = ""  # test bot token (-t --test)

# what languages does the bot support (specify in *language_code* format)
lang_support = []  # libs.src.{lang} (*other* if lang not support)

bot: types.User  # this what *get_me* function return
