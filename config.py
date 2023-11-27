import os
from dotenv import load_dotenv
# Determine the environment (default to 'dev' if not specified)
env = os.environ.get('ENVIRONMENT', 'dev')

# Load the appropriate .env file
dotenv_path = 'prod.env' if env == 'prod' else 'dev.env'
load_dotenv(dotenv_path=dotenv_path)

class AppConfig:
    def __init__(self):
        self.host = os.environ["dbhost"]
        self.user = os.environ["dbuser"]
        self.password = os.environ["dbpassword"]
        self.database = os.environ["dbdatabase"]  
        self.admin_db = os.environ["dbadmin_db"]

app_config = AppConfig()


