import logging

from aiogram import Bot, Dispatcher, types as t
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pyrogram import Client

import config

client = Client("bot", config.api_id, config.api_hash, bot_token=config.token)
bot = Bot(token=config.token, parse_mode=t.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, no_throttle_error=True)

logging.basicConfig(level=logging.WARNING)
