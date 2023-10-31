import logging

from aiogram import executor

from mongo_client import MongoClient
from tg_bot import TgBot
from config import Config

"""
  Main function, responsible for:
  - Loading configuration
  - Setting up mongo client instance
  - Running the Telegram bot
"""
def main() -> None:
  config_object = Config()

  try:
    mongo_client = MongoClient(config_object)
    tg_bot = TgBot(mongo_client, config_object)

    executor.start_polling(
      tg_bot.dispatcher, 
      skip_updates=True
    )

  except Exception as ex:
    logging.exception(f"{ex}")

# application entrypoint
if __name__ == '__main__':
  main()
