import os
from dotenv import load_dotenv
# Determine the environment (default to 'dev' if not specified)
env = os.environ.get('ENVIRONMENT', 'test')



def load_dotenv_path():
    if env=='prod':
        return 'prod.env'
    elif env == 'dev':
        return 'dev.env'
    elif env == 'devnew':
        return 'devnew.env'
    elif env == 'devv2':
        return 'devv2.env'
    elif env == 'footydebug':
        return 'footydebug.env'
    elif env == 'prodnew':
        return 'prodnew.env'
    elif env == 'prodv1':
        return 'prodv1.env'
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
        self.cache_handler = os.environ["cache_handler"]
        self.send_notifications = os.environ["send_notifications"]
        self.db_prefix = os.environ["db_prefix"]


app_config = AppConfig()


