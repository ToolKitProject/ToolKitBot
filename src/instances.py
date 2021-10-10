import config
from libs.cache import Cache
from libs.database import Database
from libs.message import MessageData

MessageData = MessageData()
Database = Database(config.sql_user, config.sql_password, config.sql_host, config.sql_database)
Cache = Cache()
