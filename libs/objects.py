import config
from libs.classes.Message import MessageData
from libs.classes.Database import Database

MessageData = MessageData()
Database = Database(config.sql_host, config.sql_user, config.sql_password, config.sql_database)
