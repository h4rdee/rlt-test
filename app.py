import pymongo, config

def main() -> None:
  config_object = config.Config()

  connection = pymongo.MongoClient(
    config_object.mongo_host, 
    config_object.mongo_port, 
    connectTimeoutMS=5000
  )

  collection = connection[config_object.database_name][config_object.collection_name]
  print(collection.find_one())

if __name__ == '__main__':
  main()
