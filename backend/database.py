from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = MongoClient(MONGO_URL)
db = client["uav_system"]
jobs = db["jobs"]

# Create index
jobs.create_index("job_id", unique=True)

print("MongoDB connected successfully")