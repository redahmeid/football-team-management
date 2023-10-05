
class AppConfig:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'sammy'
        self.password = 'password'
        self.database = 'footy'  
        self.admin_db = "mysql"
        # self.var_name = os.environ.get('VAR_NAME', 'default_value')

app_config = AppConfig()


