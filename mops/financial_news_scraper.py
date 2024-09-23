import sys
import os
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from datetime import datetime
import time

# Ensure you can import the base class
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from mops.mops_base import MopsBase

class FinancialNewsScraper(MopsBase):
    def __init__(self, data):
        super().__init__(data)
        self.stock_codes = self.df['stock_id'].tolist()
        # 記錄每個股票代碼的最新新聞資訊
        self.latest_news_tracker = {}

    def convert_time(self, date_str):
        # 民國年轉換為西元年
        year, month, day = date_str.split('/')
        ad_year = int(year) + 1911  # 民國年加 1911
        return f'{ad_year}/{month}/{day}'

    def scrape(self):
        today = datetime.now().strftime('%Y/%m/%d')  # 取得今天的日期

        for stock_code in self.stock_codes:
            try:
                print(f"正在爬取股票代碼：{stock_code}")
                self.driver.get('https://mops.twse.com.tw/mops/web/index')  # 正確的新聞頁面

                # 輸入股票代碼
                input_element = self.driver.find_element(By.ID, 'keyword')
                input_element.clear()
                input_element.send_keys(stock_code)

                # 提交表單
                self.driver.find_element(By.XPATH, '//input[@value=" 搜尋 "]').click()

                sleep(2)  # 等待頁面加載

                # 解析頁面內容
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # 找到「公司近期發布之重大訊息」的 div
                news_div = soup.find('div', class_='title_left', string='公司近期發布之重大訊息')

                if news_div:
                    # 找到該 div 之後的 table
                    table = news_div.find_next('table')

                    if table:
                        # 遍歷表格中的所有行
                        rows = table.find_all('tr')[1:]  # 跳過表頭，從第一筆數據開始
                        first_date = None  # 用於存儲最新的日期
                        latest_news = []  # 存儲當前新聞

                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 2:
                                # 1. 抓取日期
                                latest_date = cells[0].text.strip()  # 假設第一個 <td> 包含日期
                                latest_date = self.convert_time(latest_date)   # 轉換格式

                                if first_date is None:
                                    # 設置第一個日期為參考日期
                                    first_date = latest_date

                                # 只處理與第一個日期相同的新聞
                                if latest_date == first_date:
                                    # 2. 抓取快訊名稱
                                    button = cells[1].find('button')
                                    if button:
                                        news_name = button.text.strip()  # 快訊名稱
                                    else:
                                        news_name = "未知快訊名稱"

                                    # 保存當前新聞
                                    latest_news.append((latest_date, news_name))
                                else:
                                    break  # 一旦遇到不同日期的新聞，停止處理

                        # 檢查是否為新的快訊
                        if stock_code not in self.latest_news_tracker:
                            # 第一次執行，記錄最新新聞並打印
                            self.latest_news_tracker[stock_code] = latest_news
                            for date, news in latest_news:
                                message = f"日期: {date} | 快訊名稱: {news}"
                                print(message)
                        else:
                            # 對比是否有新的新聞
                            if latest_news != self.latest_news_tracker[stock_code]:
                                # 更新記錄並打印新新聞
                                self.latest_news_tracker[stock_code] = latest_news
                                for date, news in latest_news:
                                    message = f"日期: {date} | 快訊名稱: {news}"
                                    print(message)
                            else:
                                print(f"股票代碼：{stock_code} 沒有新新聞。")

                        print("\n===============================================================\n")
                    else:
                        print(f"未找到表格，股票代碼：{stock_code}")
                else:
                    print(f"未找到「公司近期發布之重大訊息」的部分，股票代碼：{stock_code}")
            except Exception as e:
                print(f"爬取股票代碼 {stock_code} 時出錯：{e}")
                continue

        

    def start_scraping(self, interval_minutes=20):
        """每隔 interval_minutes 分鐘執行一次爬取"""
        while True:
            print("開始檢查新聞...\n")
            self.scrape()
            time.sleep(interval_minutes)
        self.driver.quit()  # 關閉瀏覽器