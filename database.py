import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")

client = None

# MongoDB connection
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection error:", e)

if client:
    db = client["esports_db"]
    users_collection = db["users"]
else:
    users_collection = None
