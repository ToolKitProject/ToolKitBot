# mv config.sample.py config.py

from aiogram import types as t

token = ""
main_token = ""  # main bot token (-m --main)
test_token = ""  # test bot token (-t --test)

api_id = ""  # this can be found here https://my.telegram.org/apps
api_hash = ""  # this can be found here https://my.telegram.org/apps

bot: t.User  # this what *get_me* function return
