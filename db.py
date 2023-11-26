import pymysql
from config import app_config
import aiomysql
timeout = 10


db_config = {
    "charset":"utf8mb4",
    "connect_timeout":timeout,
    "db":app_config.database,
    "host":app_config.host,
    "password":app_config.password,
    "port":15380,
    "user":app_config.user
}

admin_db_config = {
    "charset":"utf8mb4",
    "connect_timeout":timeout,
    "db":app_config.admin_db,
    "host":app_config.host,
    "password":app_config.password,
    "port":15380,
    "user":app_config.user
}

def connection(database=app_config.admin_db):
    connection = aiomysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        db=database,
        host=app_config.host,
        password=app_config.password,
        port=15380,
        user=app_config.user,
        )
    return connection


    
  
