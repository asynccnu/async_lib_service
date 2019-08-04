import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGOHOST = os.getenv('MONGOHOST') or 'localhost'
MONGOPORT = int(os.getenv('MONGOPORT') or '27017')
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME') or "muxi"
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD') or "nopassword"

async def db_setup():
    # client = AsyncIOMotorClient(MONGODB_HOST, MONGODB_PORT)
    mongo_uri = "mongodb://{}:{}@{}:{}".format(MONGODB_USERNAME, MONGODB_PASSWORD, MONGOHOST, MONGOPORT)
    client = AsyncIOMotorClient(mongo_uri)
    attention = client['attention']
    attentioncol = attention['attentiondb']
    return attention 
