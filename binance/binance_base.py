import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from pkg.mongo import MongoConnector

class BinanceBase:

    def __init__(self):
        self.mongo = MongoConnector().get_cloud_conn()['CRYPTO']
        self.url = 'https://www.binance.com/zh-TC/support/announcement/'

        # 初始化 Chrome driver 為無頭模式
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")  # 禁用沙箱（避免某些環境中的權限問題）
        chrome_options.add_argument("--disable-dev-shm-usage")  # 避免資源限制錯誤
        self.driver = webdriver.Chrome(options=chrome_options)  # 使用共享的無頭模式
        self.driver.get(self.url)

    # def scrape(self):
    #     raise NotImplementedError

    # def update_data(self):
    #     raise NotImplementedError