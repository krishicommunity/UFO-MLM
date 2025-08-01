from pymongo import MongoClient
import os

print("✅ database.py loaded")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI is not set in environment")

print("✅ Connecting to MongoDB:", MONGO_URI)

client = MongoClient(MONGO_URI)
db = client["ufo"]

print("✅ MongoDB database 'ufo' initialized")

# Confirm export
print("✅ db object:", db)
