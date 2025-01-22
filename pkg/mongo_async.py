from config_reader import Config
import motor.motor_asyncio
import os

PROJECT_ROOT =os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATABASE_CONFIG_FILE = os.path.join(CONFIG_DIR, 'database.json')

class MongoConnector(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Avoid redundant initialization
            super().__init__()
            config = Config(DATABASE_CONFIG_FILE).load_config()
            cloud = config['mongodb']['cloud']
            local = config['mongodb']['local']
            try:
                self.cloud = motor.motor_asyncio.AsyncIOMotorClient(cloud)
            except Exception as e:
                # Handle exceptions
                pass
            try:
                self.local = motor.motor_asyncio.AsyncIOMotorClient(local)
            except Exception as e:
                # Handle exceptions
                pass
            self._initialized = True

    def get_cloud_conn(self):
        return self.cloud

    async def get_local_conn(self):
        return self.local
