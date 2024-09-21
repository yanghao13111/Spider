import os
import pandas as pd
from selenium import webdriver

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class MopsBase:
    def __init__(self, data):
        self.df = pd.read_csv(os.path.join(PROJECT_ROOT, data), dtype=str)
        self.url = 'https://mops.twse.com.tw/mops/web/index'
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    # 首次執行時，請覆寫此方法
    def scrape(self):
        raise NotImplementedError

    def update_data(self):
        raise NotImplementedError
