import config
from libs.message import MessageData
from libs.database import Database
from libs.cache import Cache

MessageData = MessageData()
Database = Database(config.sql_host, config.sql_user, config.sql_password, config.sql_database)
Cache = Cache()
