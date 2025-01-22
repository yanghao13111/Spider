import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from pkg.config_reader import Config
import requests

UTILS_ROOT = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(UTILS_ROOT, 'config')
SLACK_CONFIG_FILE = os.path.join(CONFIG_DIR, 'slack.json')

class SlackBot:
    """
    Slack Bot

    Bot Available:
    - dev: Developer Bot

    Channel Available:
    - debug: Debug Channel
    - developer: Developer Channel
    - signal: Signal Channel
    """

    def __init__(self):
        config = Config(SLACK_CONFIG_FILE).load_config()
        self.CHANNEL = config['channel']
        self.TOKEN = config['token']

    def send_message(self, bot, channel, text):
        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {self.TOKEN[bot]}"}
        data = {"channel": self.CHANNEL[channel], "text": text}
        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Error sending message: {response.text}")

        return response.json()

    def send_file(self, bot, channel, file_path):
        url = "https://slack.com/api/files.upload"
        headers = {"Authorization": f"Bearer {self.TOKEN[bot]}"}
        data = {"channels": self.CHANNEL[channel]}
        files = {"file": open(file_path, "rb")}
        response = requests.post(url, headers=headers, data=data, files=files)

        if response.status_code != 200:
            raise Exception(f"Error uploading file: {response.text}")

        return response.json()

