from aiogram import Bot, Dispatcher, types
from config import Config

class TgBot:
  @property
  def dispatcher(self):
    return self.__dispatcher

  def __init__(self, config: Config) -> None:
    self.__bot_object = Bot(token=config.tg_bot_token)
    self.__dispatcher = Dispatcher(self.__bot_object)

    @self.__dispatcher.message_handler(commands=['start', 'help'])
    async def send_welcome(message: types.Message) -> None:
      await message.reply("Hello there!")
    
    @self.__dispatcher.message_handler()
    async def message_handler(message: types.Message):
      await message.reply(message.text)
