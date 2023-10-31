import json, logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BadRequest

from mongo_client import MongoClient
from config import Config

class TgBot:
  """
  Telegram bot class

  Attributes:
    __bot_object (aiogram.Bot): Telegram bot object
    __dispatcher (aiogram.Dispatcher): Dispatcher object for handling bot messages
    __mongo_client (MongoClient): MongoDB client object
  """

  """
  Getter for the __dispatcher attribute

  Returns:
    Dispatcher: The Dispatcher object
  """
  @property
  def dispatcher(self):
    return self.__dispatcher

  """
  TgBot class constructor

  Args:
    mongo_client (MongoClient): MongoDB client object
    config (Config): Configuration object
  """
  def __init__(self, mongo_client: MongoClient, config: Config) -> None:
    self.__bot_object = Bot(token=config.tg_bot_token)
    self.__dispatcher = Dispatcher(self.__bot_object)
    self.__mongo_client = mongo_client

    """
    Handler for '/start' and '/help' commands

    Args:
      message (types.Message): Incoming message object
    """
    @self.__dispatcher.message_handler(commands=['start', 'help'])
    async def send_welcome(message: types.Message) -> None:
      await message.reply(
        "Please, provide an input data in `json` format", 
        parse_mode="MarkdownV2"
      )
    
    """
    Handler for incoming messages

    Args:
      message (types.Message): Incoming message object
    """
    @self.__dispatcher.message_handler()
    async def message_handler(message: types.Message):
      try:
        json_object = json.loads(message.text)

        # basic sanity check..
        if type(json_object) is not dict or \
          not "dt_from" in json_object.keys():
            raise ValueError(message.text)

        result = "```json\n"
        result += json.dumps(
          mongo_client.get_aggregated_data(
            json_object["dt_from"],
            json_object["dt_upto"],
            json_object["group_type"]
          ), indent=2
        )
        result += "\n```"

        await message.reply(
          result,
          parse_mode="MarkdownV2"
        )

      # handle invalid user input by saying whats exactly wrong..
      except ValueError as ex:
        logging.warning(f"got invalid input data: {ex}")

        await message.reply(
          "Provided input data is invalid\n"
          "Consider trying following data:\n"
          '```json\n{\n  "dt_from": "2022-09-01T00:00:00",\n  "dt_upto": "2022-12-31T23:59:00",\n  "group_type": "month"\n}\n```', 
          parse_mode="MarkdownV2"
        )

      # oops.. seems like we hit telegram's message limits
      except BadRequest as ex:
        logging.error(ex)

        await message.reply(
          "Sorry, that's too much of the data 😔\n"
          "You can try lesser date period or change the `group_type`",
          parse_mode="MarkdownV2"
        )
