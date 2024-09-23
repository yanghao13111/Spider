import sys
import os
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from datetime import datetime

# Ensure you can import the base class
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from mops.mops_base import MopsBase

class FinancialNewsScraper(MopsBase):
    def __init__(self, data):
        super().__init__(data)
        self.stock_codes = self.df['stock_id'].tolist()

    def convert_time(self, date_str):
        # 民國年轉換為西元年
        year, month, day = date_str.split('/')
        ad_year = int(year) + 1911  # 民國年加 1911
        return f'{ad_year}/{month}/{day}'

    def scrape(self):
        today = datetime.now().strftime('%Y/%m/%d')  # Get today's date

        for stock_code in self.stock_codes:
            try:
                print(f"正在爬取股票代碼：{stock_code}")
                self.driver.get('https://mops.twse.com.tw/mops/web/index')  # Correct page for news

                # Input stock code
                input_element = self.driver.find_element(By.ID, 'keyword')
                input_element.clear()
                input_element.send_keys(stock_code)

                # Submit the form
                self.driver.find_element(By.XPATH, '//input[@value=" 搜尋 "]').click()

                # Wait for the page to load
                sleep(2)

                # Parse the page content
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # 找到「公司近期發布之重大訊息」的 div
                news_div = soup.find('div', class_='title_left', text='公司近期發布之重大訊息')
                
                if news_div:
                    # 找到該 div 之後的 table
                    table = news_div.find_next('table')
                    
                    if table:
                        # 遍歷表格中的所有行
                        rows = table.find_all('tr')[1:]  # 跳過表頭，從第1筆數據開始
                        first_date = None  # 用於存儲最新的日期

                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 2:
                                # 1. 抓取日期
                                latest_date = cells[0].text.strip()  # 假設第一個 `<td>` 包含日期
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

                                    # 3. 整合日期和快訊名稱成一個訊息
                                    message = f"日期: {latest_date} | 快訊名稱: {news_name}"

                                    # 4. 打印整合的訊息
                                    print(message)

                                    # 如果是今天的新聞，打印即時快訊
                                    if latest_date == today:
                                        print(f"{message} - 即時快訊！")
                                else:
                                    # 一旦遇到與第一個日期不相符的新聞，停止處理
                                    break
                            else:
                                print(f"無法找到日期或快訊名稱，股票代碼：{stock_code}")
                    
                        print("\n===============================================================\n")                    
                    else:
                        print(f"未找到表格，股票代碼：{stock_code}")
                else:
                    print(f"未找到「公司近期發布之重大訊息」的部分，股票代碼：{stock_code}")
            except Exception as e:
                print(f"爬取股票代碼 {stock_code} 時出錯：{e}")
                continue

        # Close the browser
        self.driver.quit()
