import os
from dotenv import load_dotenv
load_dotenv()

class AppConfig:
    def __init__(self):
        self.host = os.environ["dbhost"]
        self.user = os.environ["dbuser"]
        self.password = os.environ["dbpassword"]
        self.database = os.environ["dbdatabase"]  
        self.admin_db = os.environ["dbadmin_db"]

app_config = AppConfig()


