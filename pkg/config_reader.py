import json


class Config(object):
    _instances = {}

    def __new__(cls, config_path):
        if config_path not in cls._instances:
            cls._instances[config_path] = super(Config, cls).__new__(cls)
            instance = cls._instances[config_path]
            instance.config_file_path = config_path
            instance.config = None
        return cls._instances[config_path]

    def load_config(self):
        if self.config is None:
            with open(self.config_file_path) as f:
                self.config = json.load(f)
        return self.config