import logging

import config
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram import executor
from aiogram import types as t
import optparse

parser = optparse.OptionParser(conflict_handler="resolve")
parser.add_option('-t', '--test',
                  action="store_true",
                  dest='test',
                  help='test token')
parser.add_option('-m', '--main',
                  action="store_true",
                  dest='main',
                  help='main token')
values, args = parser.parse_args()

if values.test:
    config.token = config.test_token
elif values.main:
    config.token = config.main_token
else:
    raise ValueError("АРГУМЕНТЫ СУКА")

from bot import dp, client
import handlers
from libs.objects import MessageData
import lang_conf


async def shutdown(dp: Dispatcher):
    await MessageData.close()


async def startup(dp: Dispatcher):
    await client.start()
    for lang, src in lang_conf.lang_map.items():
        for scope, cmd in src.any.command_list.items():
            if lang == "other": lang = None
            await dp.bot.set_my_commands(cmd, scope, lang)
    config.bot = await dp.bot.get_me()
    logging.info("Bot init")


if __name__ == "__main__":
    executor.start_polling(
        dp,
        on_startup=startup,
        on_shutdown=shutdown,
        allowed_updates=t.AllowedUpdates.all()
    )
