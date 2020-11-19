from service import app, loop, web
from service.api import api
from service.database import db_setup

attention = loop.run_until_complete(db_setup())
api['attention'] = attention

if __name__ == '__main__':
   web.run_app(app, host="127.0.0.1", port=1111)
