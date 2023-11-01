import pymongo, logging
from datetime import datetime, timezone, timedelta

class MongoClient:
  """
  A MongoDB client class that connects to a MongoDB server and retrieves data from a collection

  Attributes:
    __connection (pymongo.MongoClient): The MongoDB client object
    __database (pymongo.database.Database): The MongoDB database object
    __collection (pymongo.collection.Collection): The MongoDB collection object
  """

  __connection: pymongo.MongoClient = None
  __database: pymongo.database.Database = None
  __collection: pymongo.collection.Collection = None

  """
  Connects to a MongoDB server using the given hostname and port number
  Raises an exception if the connection fails
  
  Args:
    host (str): The hostname of the MongoDB server
    port (int): The port number of the MongoDB server

  Returns:
    A pymongo.MongoClient object representing the MongoDB connection
  """
  def __connect_to_mongo(self, host: str, port: int) -> pymongo.MongoClient:
    connection = pymongo.MongoClient(host, port, connectTimeoutMS=5000)
    if connection is None:
      raise Exception(f"failed to connect to ({host}:{port})")
    return connection

  """
  Gets a MongoDB database instance from a connection by name
  Raises an exception if the database is not found

  Args:
    database_name (str): The name of the MongoDB database to retrieve

  Returns:
    A pymongo.database.Database object representing the database instance
  """
  def __get_database(self, database_name: str) -> pymongo.database.Database:
    if not database_name in self.__connection.list_database_names():
      raise Exception(f"couldn't find {database_name} database")
    return self.__connection[database_name]

  """
  Gets a MongoDB collection instance from a database by name
  Raises an exception if the collection is not found

  Args:
    collection_name (str): The name of the MongoDB collection to retrieve

  Returns:
    A pymongo.collection.Collection object representing the collection instance
  """
  def __get_collection(self, collection_name: str) -> pymongo.collection.Collection:
    if not collection_name in self.__database.list_collection_names():
      raise Exception(f"couldn't find {collection_name} collection in {self.__database.name}")
    return self.__database[collection_name]

  def __init__(self, config_object) -> None:
    try: # setup the mongo db client instance, then get a collection from the db
        self.__connection = self.__connect_to_mongo(
          config_object.mongo_host, 
          config_object.mongo_port
        )

        self.__database = self.__get_database(config_object.database_name)
        self.__collection = self.__get_collection(config_object.collection_name)

    except Exception as ex:
      logging.exception(ex)
      self.__connection.close()
  
  """
  Fills missing database entries

  Args:
    dt_from (str): The start time of the time range in ISO-8601 format
    dt_upto (str): The end time of the time range in ISO-8601 format

  Returns:
    Nothing
  """
  def __fill_missing_dates(self, dt_from: str, dt_upto: str) -> None:
    date_from = datetime.strptime(dt_from, "%Y-%m-%dT%H:%M:%S")
    date_upto = datetime.strptime(dt_upto, "%Y-%m-%dT%H:%M:%S")
    current_date = date_from

    while current_date <= date_upto:
        # Check if a document for the current date exists
        if self.__collection.count_documents({'dt': current_date}) == 0:
            # Insert a dummy document for the missing date
            self.__collection.insert_one({'dt': current_date, 'value': 0})
        current_date += timedelta(days=1)

  """
  Aggregates data from a MongoDB collection based on the given time range and group type
  Returns a dictionary with the dataset and labels for the aggregated data

  Args:
    dt_from (str): The start time of the time range in ISO-8601 format
    dt_upto (str): The end time of the time range in ISO-8601 format
    group_type (str): The grouping type for the aggregation (either `hour`, `day` or `month`)

  Returns:
    A dictionary containing the dataset and labels for the aggregated data
  """
  def get_aggregated_data(self, dt_from: str, dt_upto: str, group_type: str) -> dict:
    if self.__collection is None: # fool-proofing this..
      if self.__connection:
        self.__connection.close()
      raise Exception("tried to aggregate data without proper client initialization")

    # convert the timestamp strings to datetime objects with UTC time zone
    def convert_time_to_tz(dt: str) -> datetime:
      return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")\
        .replace(tzinfo=timezone.utc).astimezone()
    
    # get the MongoDB aggregation grouping pipeline stage based on the group type
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

      else: # if `group_type` is unknown treat it like `month` to avoid ub
        logging.warning(f"unknown grouping: {group_type}, will group by `month` by default")
        grouping['$group']['_id']['$dateToString']['format'] = "%Y-%m-01T00:00:00"
  
      return grouping

    self.__fill_missing_dates(dt_from, dt_upto)

    # setup the MongoDB aggregation pipeline
    pipeline = [
      { # match based on the provided time
        '$match': {
          'dt': {
            '$gte': convert_time_to_tz(dt_from),
            '$lte': convert_time_to_tz(dt_upto)
          }
        }
      },
      get_grouping(group_type), # group
      {'$sort': { '_id': 1 }} # sort results
    ]

    # execute the MongoDB aggregation pipeline
    results = list(self.__collection.aggregate(pipeline))

    # extract the dataset and labels from the aggregation results
    labels = [result["_id"] for result in results]
    dataset = [result["sum"] for result in results]

    # return a dictionary containing the dataset and labels
    return {"dataset": dataset, "labels": labels}
