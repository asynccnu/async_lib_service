from service import app, web, loop 
from service.database import db_setup
from service.api import api


attention = loop.run_until_complete(db_setup())
api['attention'] = attention

if __name__ == '__main__':
    web.run_app(app) 