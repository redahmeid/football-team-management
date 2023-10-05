import os
from dotenv import load_dotenv
load_dotenv()

class AppConfig:
    def __init__(self):
        self.host = os.environ["db.host"]
        self.user = os.environ["db.user"]
        self.password = os.environ["db.password"]
        self.database = os.environ["db.database"]  
        self.admin_db = os.environ["db.admin_db"]

app_config = AppConfig()


