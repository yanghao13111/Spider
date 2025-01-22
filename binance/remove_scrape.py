import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from datetime import datetime
from pkg.slack import SlackBot
import time  # 用於設置等待時間
import pytz 
from pymongo import errors
from binance.binance_base import BinanceBase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException




class RemoveInfoScraper(BinanceBase):

    def __init__(self):
        super().__init__()
        self.mongo_collection = self.mongo['remove_info']
        self.mongo_collection.create_index(
            [("date", 1), ("news_name", 1)],
            unique=True
        )

    # def convert_time(self, date_str):
    #     # 民國年轉換為西元年
    #     year, month, day = date_str.split('/')
    #     ad_year = int(year) + 1911  # 民國年加 1911
    #     return f'{ad_year}/{month}/{day}'
    
    def save_to_mongodb(self, date, news_name, signal):
        # 構建 MongoDB 中的 document 資料，加入 company_name
        document = {
            "date": date,
            "news_name": news_name,
            "signal": signal,
            "scraped_time": datetime.now()
        }
        try:
            # 插入到 MongoDB，重複資料將不會插入
            self.mongo_collection.insert_one(document)
            return True  # 成功插入新資料
        except errors.DuplicateKeyError:
            print(f'{date} {news_name} 資料已存在，不需重複插入')
            return False  # 資料已存在，不需重複插入
        
    # def scrape(self):
