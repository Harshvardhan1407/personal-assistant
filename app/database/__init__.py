from pymongo import MongoClient
from .database_config import host, port, database_name, collection_name
# Connect to MongoDB
client = MongoClient(f"mongodb://{host}:{port}/")  # Update with your MongoDB URI
db = client[database_name]
mongo_collection = db[collection_name]    
