import pymongo, logging

from datetime import datetime, timezone

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
      logging.exception(ex)
      self.__connection.close()

  def get_aggregated_data(self, dt_from: str, dt_upto: str, group_type: str) -> dict:
    if self.__collection is None:
      if self.__connection:
        self.__connection.close()
      raise Exception("tried to aggregate data without proper client initialization")

    def convert_time_to_tz(dt: str) -> datetime:
      return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")\
        .replace(tzinfo=timezone.utc).astimezone()

    def get_grouping(group_type: str) -> dict:
      grouping = {
        '$group': {
          '_id': {
            '$dateToString': {
              'format': '', 
              'date': '$dt'
            }
          }, 
          'sum': { '$sum': '$value' }
        }
      }

      """
      match .. case is more suitable here, but
      my interpreter version is 3.8.10, so i guess
      we gonna do that classic way..
      """
      if group_type == "hour":
        grouping['$group']['_id']['$dateToString']['format'] = "%Y-%m-%d %HT00:00:00"

      elif group_type == "day":
        grouping['$group']['_id']['$dateToString']['format'] = "%Y-%m-%dT00:00:00"

      elif group_type == "month":
        grouping['$group']['_id']['$dateToString']['format'] = "%Y-%m-01T00:00:00"

      else:
        logging.warning(f"unknown grouping: {group_type}, will group by `month` by default")
        grouping['$group']['_id']['$dateToString']['format'] = "%Y-%m-01T00:00:00"
  
      return grouping

    pipeline = [
      {
        '$match': {
          'dt': {
            '$gte': convert_time_to_tz(dt_from),
            '$lte': convert_time_to_tz(dt_upto)
          }
        }
      },
      get_grouping(group_type),
      {'$sort': { '_id': 1 }}
    ]

    results = list(self.__collection.aggregate(pipeline))

    labels = [result["_id"] for result in results]
    dataset = [result["sum"] for result in results]

    return {"dataset": dataset, "labels": labels}
