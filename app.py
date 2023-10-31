import logging

from aiogram import executor

from mongo_client import MongoClient
from tg_bot import TgBot
from config import Config

def main() -> None:
  config_object = Config()

  try:
    mongo_client = MongoClient(config_object)
    tg_bot = TgBot(config_object)

    print(mongo_client.get_aggregated_data(
      "2022-09-01T00:00:00",
      "2022-12-31T23:59:00",
      "month"
    ))

    executor.start_polling(
      tg_bot.dispatcher, 
      skip_updates=True
    )

  except Exception as ex:
    logging.exception(f"{ex}")

if __name__ == '__main__':
  main()
