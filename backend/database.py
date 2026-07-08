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
search_cache = db["search_cache"]


async def init_indexes():
    await users_collection.create_index("email", unique=True)
    await search_cache.create_index("query", unique=True)
    await search_cache.create_index("cached_at", expireAfterSeconds=3600)  # TTL: 1 hour
