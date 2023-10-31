import pymongo

def main() -> None:
  connection = pymongo.MongoClient("localhost", 27017, connectTimeoutMS=5000)
  collection = connection["db"]["sample_collection"]
  print(collection.find_one())
  # raise NotImplementedError("Nothing is implemented yet:(")

if __name__ == '__main__':
  main()
