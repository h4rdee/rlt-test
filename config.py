"""
In production i would've used .env & secrets,
but for that test task simple json config and
a wrapper-class like this will do just fine
"""

import json, logging, os

class Config:
  """
  A configuration class that loads configuration data from a JSON file

  Attributes:
    mongo_host (str): The hostname of the MongoDB server
    mongo_port (int): The port number of the MongoDB server
    database_name (str): The name of the MongoDB database to use
    collection_name (str): The name of the MongoDB collection to use
  """

  """
  Getter for the __mongo_host attribute

  Returns:
    str: The hostname of the MongoDB server
  """
  @property
  def mongo_host(self) -> str:
    return self.__mongo_host
  
  """
  Getter for the __mongo_port attribute

  Returns:
    int: The port number of the MongoDB server
  """
  @property
  def mongo_port(self) -> int:
    return self.__mongo_port
  
  """
  Getter for the __database_name attribute

  Returns:
    str: The name of the MongoDB database to use
  """
  @property
  def database_name(self) -> str:
    return self.__database_name

  """
  Getter for the __collection_name attribute

  Returns:
    str: The name of the MongoDB collection to use
  """
  @property
  def collection_name(self) -> str:
    return self.__collection_name
  
  """
  Getter for the __tg_bot_token attribute

  Returns:
    str: The token of the Telegram bot to use
  """
  @property
  def tg_bot_token(self) -> str:
    return self.__tg_bot_token

  """
  Config class constructor
  Loads configuration data from a JSON file
  """
  def __init__(self) -> None:
    json_object = None

    try:
      with open(
        os.path.join(
          os.getcwd(),
          "rlt-test",
          "config.json",
        ), "r"
      ) as f:
        json_object = json.load(f)

    except Exception as ex:
      logging.warning(ex)

    self.__mongo_host = "localhost" \
      if not "mongo_host" in json_object \
        else json_object["mongo_host"]

    self.__mongo_port = 27017 \
      if not "mongo_port" in json_object \
        else json_object["mongo_port"]

    self.__database_name = "db" \
      if not "database_name" in json_object \
        else json_object["database_name"]

    self.__collection_name = "sample_collection" \
      if not "collection_name" in json_object \
        else json_object["collection_name"]
    
    self.__tg_bot_token = "" \
      if not "tg_bot_token" in json_object \
        else json_object["tg_bot_token"]

    if self.__tg_bot_token == "": # try to get token from env
      self.__tg_bot_token = os.environ.get('TG_BOT_TOKEN')
