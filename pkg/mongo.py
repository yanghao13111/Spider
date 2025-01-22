import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from pkg.config_reader import Config
from pymongo import MongoClient

UTILS_ROOT = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(UTILS_ROOT, 'config')
DATABASE_CONFIG_FILE = os.path.join(CONFIG_DIR, 'database.json')

class MongoConnector(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path=DATABASE_CONFIG_FILE):
        if self._instance is not None:  # Avoid redundant initialization
            super().__init__()
            config = Config(config_path).load_config()
            cloud = config['mongodb']['cloud']
            local = config['mongodb']['local']
            try:
                self.cloud = MongoClient(cloud)
            except Exception as e:
                # Handle exceptions
                pass
            try:
                self.local = MongoClient(local)
            except Exception as e:
                # Handle exceptions
                pass
            self._initialized = True

    def get_cloud_conn(self):
        return self.cloud

    def get_local_conn(self):
        return self.local