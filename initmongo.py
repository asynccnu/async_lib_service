from service import app, web, loop 
from service.database import db_setup
from service.api import api


if __name__ ==  '__main__' :
    attention = loop.run_until_complete(db_setup())
    api['attention'] = attention