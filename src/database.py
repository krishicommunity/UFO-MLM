from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")  # Make sure this is set correctly in Render
client = MongoClient(MONGO_URI)
db = client["ufo"]

print("✅ MONGO_URI =", MONGO_URI)
print("✅ DB initialized:", db)
