import logging
import optparse
import signal

from aiogram import executor
from aiogram import types as t
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.utils import json as aiogram_json
import json

import config

parser = optparse.OptionParser(conflict_handler="resolve")
parser.add_option('-t', '--test',
                  action="store_true",
                  dest='test',
                  help='Start with test token')
parser.add_option('-m', '--main',
                  action="store_true",
                  dest='main',
                  help='Start with main token')
parser.add_option('-i', '--init-commands',
                  action="store_true",
                  dest='commands',
                  help='Re init bot commands')
values, args = parser.parse_args()

if values.test:
    config.token = config.test_token
elif values.main:
    config.token = config.main_token
else:
    config.token = config.test_token

from bot import dp, client
import libs
import src
import locales
import handlers

other = locales.other
MessageData = src.instances.MessageData
langs = locales.langs
locales = libs.locales
NewInstance = src.utils.NewInstance
LogMiddleware = src.utils.LogMiddleware


def close(signal: int, frame):
    logging.warning(f"Handling signal ({signal})")
    exit()


async def shutdown(dp: Dispatcher):
    logging.warning("Delete MessageData")
    await MessageData.close()
    await client.stop()
    logging.warning(f"Bot stopped")


async def startup(dp: Dispatcher):
    config.bot = await dp.bot.get_me()
    src.instances.Database.get_user(config.bot.id)

    logging.warning("Start client")
    await client.start()

    if values.main or values.commands:
        logging.warning("Init commands")
        try:
            await other.command_list.set()
            for l in langs:
                locales.lang = l
                await other.command_list.set()
        except Exception as e:
            logging.error(f"Init command failed ({e})")

    logging.warning("Bot initialized")


def dumps(data):
    return json.dumps(data, ensure_ascii=False, cls=locales.TextEncoder)


if __name__ == "__main__":
    aiogram_json.dumps = dumps
    signal.signal(signal.SIGTERM, close)
    dp.setup_middleware(NewInstance())
    dp.setup_middleware(LogMiddleware())

    executor.start_polling(
        dp,
        on_startup=startup,
        on_shutdown=shutdown,
        allowed_updates=t.AllowedUpdates.all()
    )
