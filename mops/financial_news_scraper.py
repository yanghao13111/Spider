import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from datetime import datetime
from pkg.slack import SlackBot
import time  # 用於設置等待時間
from pymongo import errors
from twse.mops.mops_base import MopsBase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class FinancialNewsScraper(MopsBase):

    def __init__(self, source_path, channel):
        super().__init__(source_path)
        self.channel = channel
        self.stock_codes = self.df['stock_id'].tolist()
        self.last_scraped_time = None  # 用來記錄最後檢查的時間
        self.mongo_collection = self.mongo['twse_mops']
        self.mongo_collection.create_index(
            [("date", 1), ("stock_code", 1), ("news_name", 1)],
            unique=True
        )

    def convert_time(self, date_str):
        # 民國年轉換為西元年
        year, month, day = date_str.split('/')
        ad_year = int(year) + 1911  # 民國年加 1911
        return f'{ad_year}/{month}/{day}'
    
    def save_to_mongodb(self, stock_code, company_name, date, news_name):
        # 構建 MongoDB 中的 document 資料，加入 company_name
        document = {
            "stock_code": stock_code,
            "company_name": company_name,
            "date": date,
            "news_name": news_name,
            "scraped_time": datetime.now()
        }
        try:
            # 插入到 MongoDB，重複資料將不會插入
            self.mongo_collection.insert_one(document)
            return True  # 成功插入新資料
        except errors.DuplicateKeyError:
            print(f"資料已存在，不需重複插入，股票代碼：{stock_code}，日期：{date}，快訊名稱：{news_name}")
            return False  # 資料已存在，不需重複插入

    # 根據是否傳入參數來區分主動查詢與自動訂閱
    def scrape(self, *custom_stock_codes):
        # 如果有傳入 custom_stock_codes，則視為主動查詢；若無，則視為訂閱模式
        is_manual = len(custom_stock_codes) > 0

        # 如果沒有提供 custom_stock_codes，則使用全局的 self.stock_codes
        stock_codes = custom_stock_codes if is_manual else self.stock_codes
        
        today = datetime.now().strftime('%Y/%m/%d')  # Get today's date
        for stock_code in stock_codes:
            try:
                print(f"正在爬取股票代碼：{stock_code}")
                self.driver.get('https://mops.twse.com.tw/mops/web/index')  # Correct page for news

                # 等待 dialog-mask 消失或移除它
                try:
                    WebDriverWait(self.driver,30).until(
                        EC.invisibility_of_element((By.ID, 'dialog-mask'))
                    )
                except TimeoutException:
                    print(f"等待 dialog-mask 消失超時，跳過股票代碼：{stock_code}")
                    continue

                # 移除遮罩元素，如果仍然存在
                self.driver.execute_script("""
                    var element = document.getElementById("dialog-mask");
                    if (element) {
                        element.parentNode.removeChild(element);
                    }
                """)

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

                # 找到公司名稱
                company_name_input = soup.find('input', {'id': 'COMPANY_NAME'})
                if company_name_input:
                    company_name = company_name_input.get('value', '未知公司名稱')  # 抓取公司名稱
                else:
                    company_name = '未知公司名稱'

                # 找到「公司近期發布之重大訊息」的 div
                news_div = soup.find('div', class_='title_left', string='公司近期發布之重大訊息')

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

                                    # 3. 保存資料到 MongoDB，並判斷是否為新資料
                                    is_new_news = self.save_to_mongodb(stock_code, company_name, latest_date, news_name)

                                    # 只有在插入新資料的情況下才發送到 Slack
                                    if is_new_news:
                                        # 根據是否是主動查詢來決定前綴
                                        prefix = "[主動查詢]" if is_manual else ""
                                        message = f"{prefix} 日期: {latest_date} | 公司名稱: {company_name} | 快訊名稱: {news_name}"

                                        # 如果是今天的新聞，打印即時快訊
                                        if latest_date == today:
                                            print(f"{message} - 即時快訊！")
                                            SlackBot().send_message(
                                                bot = 'dev', 
                                                channel = self.channel, 
                                                text = f'```[{company_name}]\n{message} - 即時快訊！❗️❗️❗️```'
                                            )
                                        else:
                                            print(message)
                                            SlackBot().send_message(
                                                bot = 'dev', 
                                                channel = self.channel, 
                                                text = f'```[❗️❗️❗️{company_name+" "+stock_code} 🌏🌏🌏 ]\n{message}```')
                                else:
                                    break  # 一旦遇到不同日期的新聞，停止處理
                            else:
                                print(f"無法找到日期或快訊名稱，股票代碼：{stock_code}")
                                SlackBot().send_message('dev', 'dev', f'```無法找到日期或快訊名稱，股票代碼：{stock_code}```')
                    else:
                        print(f"未找到表格，股票代碼：{stock_code}")
                        SlackBot().send_message('dev', 'debug', f'```未找到表格，股票代碼：{stock_code}```')
                else:
                    print(f"未找到「公司近期發布之重大訊息」的部分，股票代碼：{stock_code}")
                    SlackBot().send_message('dev', 'debug', f'```未找到「公司近期發布之重大訊息」的部分，股票代碼：{stock_code}```')
                print("\n===============================================\n")

            except Exception as e:
                print(f"爬取股票代碼 {stock_code} 時出錯：{e}")
                SlackBot().send_message('dev', 'debug', f'```爬取股票代碼 {stock_code} 時出錯：{e}```')
                continue
