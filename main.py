import config
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram import executor
import optparse
import logging


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

if True:
    from bot import dp, client
    import handlers
    from libs.objects import MessageData
    from libs.src.system import commands

    # from objects import MessageData


async def shutdown(dp: Dispatcher):
    await MessageData.close()


async def startup(dp: Dispatcher):
    await client.start()
    await dp.bot.set_my_commands(commands)
    config.bot = await dp.bot.get_me()
    logging.warning(
        f"{config.bot.full_name} [{config.bot.mention}]")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=startup, on_shutdown=shutdown)
