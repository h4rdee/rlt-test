"""
In production i would've used .env & secrets,
but for that test task simple json config and
a wrapper-class like this will do just fine
"""

import json, logging, os

class Config:
  @property
  def mongo_host(self) -> str:
    return self.__mongo_host

  @property
  def mongo_port(self) -> int:
    return self.__mongo_port
  
  @property
  def database_name(self) -> str:
    return self.__database_name

  @property
  def collection_name(self) -> str:
    return self.__collection_name
  
  @property
  def tg_bot_token(self) -> str:
    return self.__tg_bot_token

  def __init__(self) -> None:
    json_object = None

    try:
      with open(
        os.path.join(
          os.getcwd(), 
          "rlt-test", 
          "config.json"
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
