import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "tol_mol_ke_bol")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
