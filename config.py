import os
from dotenv import load_dotenv
# Determine the environment (default to 'dev' if not specified)
env = os.environ.get('ENVIRONMENT', 'test')



def load_dotenv_path():
    if env=='prod':
        return 'prod.env'
    elif env == 'dev':
        return 'dev.env'
    else:
        return 'test.env'
# Load the appropriate .env file
dotenv_path = load_dotenv_path()

load_dotenv(dotenv_path=dotenv_path)

class AppConfig:
    def __init__(self):
        self.host = os.environ["dbhost"]
        self.user = os.environ["dbuser"]
        self.password = os.environ["dbpassword"]
        self.database = os.environ["dbdatabase"]  
        self.admin_db = os.environ["dbadmin_db"]
        self.email_token = os.environ["email_token"]



app_config = AppConfig()


