from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")

print("✅ database.py loaded")
print("✅ MONGO_URI:", MONGO_URI)

if MONGO_URI is None:
    raise Exception("❌ MONGO_URI environment variable is NOT SET!")

client = MongoClient(MONGO_URI)
db = client["ufo"]

print("✅ DB Connection initialized:", db)
