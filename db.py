import pymysql
from config import app_config
timeout = 10


def connection(database=app_config.admin_db):
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=database,
        host=app_config.host,
        password=app_config.password,
        read_timeout=timeout,
        port=15380,
        user=app_config.user,
        write_timeout=timeout,
        )
    return connection
    
  
