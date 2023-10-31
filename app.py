import pymongo

from aiogram import executor

from config import Config
from tg_bot import TgBot

def main() -> None:
  config_object = Config()
  tg_bot = TgBot(config_object)

  executor.start_polling(
    tg_bot.dispatcher, 
    skip_updates=True
  )

if __name__ == '__main__':
  main()
