import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGOHOST = os.getenv('MONGOHOST') or 'localhost'
MONGOPORT = int(os.getenv('MONGOPORT') or '27017')

async def db_setup():
    client = AsyncIOMotorClient(MONGOHOST, MONGOPORT)
    attention = client['attention']
    attentioncol = attention['attention']
    return attention 
