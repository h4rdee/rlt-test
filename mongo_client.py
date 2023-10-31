import pymongo, logging

class MongoClient:
  __connection: pymongo.MongoClient = None
  __database: pymongo.database.Database = None
  __collection: pymongo.collection.Collection = None

  def __connect_to_mongo(self, host: str, port: int) -> pymongo.MongoClient:
    connection = pymongo.MongoClient(host, port, connectTimeoutMS=5000)
    if connection is None:
      raise Exception(f"failed to connect to ({host}:{port})")
    return connection

  def __get_database(self, database_name: str) -> pymongo.database.Database:
    if not database_name in self.__connection.list_database_names():
      raise Exception(f"couldn't find {database_name} database")
    return self.__connection[database_name]

  def __get_collection(self, collection_name: str) -> pymongo.collection.Collection:
    if not collection_name in self.__database.list_collection_names():
      raise Exception(f"couldn't find {collection_name} collection in {self.__database.name}")
    return self.__database[collection_name]

  def __init__(self, config_object) -> None:
    try:
        self.__connection = self.__connect_to_mongo(
          config_object.mongo_host, 
          config_object.mongo_port
        )

        self.__database = self.__get_database(config_object.database_name)
        self.__collection = self.__get_collection(config_object.collection_name)

    except Exception as ex:
      logging.exception(f"{ex}")
      self.__connection.close()

  def test(self) -> dict:
    if self.__collection is not None:
      return self.__collection.find_one()
