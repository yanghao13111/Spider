import sys
import os
PROJECT_ROOT = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)


from tdcc.tdcc_base import TdccBase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from typing import List

DATADIR = os.path.dirname((os.path.dirname(os.path.abspath(__file__)))) + '/database'


class EquityDispersionTable(TdccBase):
    def __init__(self, data):
        super().__init__(data)
        self.stock_codes = self.df['證券代號'].tolist()

    def scrape(self):
        dates = [date.get_attribute('value') for date in Select(self.driver.find_element(By.ID, 'scaDate')).options]
        batch_size = 2  # 每批處理的股票數量
        batch_count = 0  # 初始化批次計數器
        stock_data = []  # 初始化股票數據緩存

        for stock_code in self.stock_codes:
            for date in dates:
                print(stock_code, date)
                # ---------------------- date ----------------------
                select_element = Select(self.driver.find_element(By.ID, 'scaDate'))
                select_element.select_by_value(date)
                # ---------------------- stock code ----------------------
                input_element = self.driver.find_element(By.ID, 'StockNo')
                input_element.clear() 
                input_element.send_keys(stock_code)
                input_element.send_keys(Keys.RETURN)


                sleep(0.3)
                data = self.driver.page_source
                soup = BeautifulSoup(data, 'html.parser')

                # ----------------------------------------table----------------------------------------
                table_div = soup.find('div', class_='table-responsive')
                table = table_div.find('table')
                rows = []
                thead = table.find('thead')
                header_cells = thead.find_all('th')
                header = [cell.text.strip() for cell in header_cells]
                rows.append(header)
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells:
                        rows.append([cell.text.strip() for cell in cells])

                if len(rows) > 1 and rows[1][0] != "查無此資料":
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                    df['股票代碼'] = stock_code
                    df['日期'] = pd.to_datetime(date, format='%Y%m%d')
                    df.drop(columns='序', inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    stock_data.append(df)
               
            batch_count += 1
            print(batch_count, batch_size, len(stock_data))
            if batch_count == batch_size:
                print("update data to parquet")
                self.update_data_to_parquet(stock_data)
                batch_count = 0
                stock_data = []
        
        self.update_data_to_parquet(stock_data)
        input("Press any key to quit...")
        self.driver.quit()

    def update_data(self, date=None):
        dates = [date.get_attribute('value') for date in Select(self.driver.find_element(By.ID, 'scaDate')).options]

        if date:
            print(date)
            if date in dates:
                latest_date = date
            else:
                latest_date = dates[0]
        else:
            latest_date = dates[0]
        print(latest_date)

        batch_size = 100  # 每批處理的股票數量
        batch_count = 0  # 初始化批次計數器
        stock_data = []  # 初始化股票數據緩存

        for stock_code in self.stock_codes:
            # ---------------------- date ----------------------
            select_element = Select(self.driver.find_element(By.ID, 'scaDate'))
            select_element.select_by_value(latest_date)
            print(stock_code, select_element.first_selected_option.text)
            # ---------------------- stock code ----------------------
            input_element = self.driver.find_element(By.ID, 'StockNo')
            input_element.clear() 
            input_element.send_keys(stock_code)
            input_element.send_keys(Keys.RETURN)

            sleep(0.2)
            data = self.driver.page_source
            soup = BeautifulSoup(data, 'html.parser')

            # ----------------------------------------table----------------------------------------
            table_div = soup.find('div', class_='table-responsive')
            table = table_div.find('table')
            rows = []
            thead = table.find('thead')
            header_cells = thead.find_all('th')
            header = [cell.text.strip() for cell in header_cells]
            rows.append(header)
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if cells:
                    rows.append([cell.text.strip() for cell in cells])

            if len(rows) > 1 and rows[1][0] != "查無此資料":
                df = pd.DataFrame(rows[1:], columns=rows[0])
                df['股票代碼'] = stock_code
                df['日期'] = pd.to_datetime(latest_date, format='%Y%m%d')
                df.drop(columns='序', inplace=True)
                df.reset_index(drop=True, inplace=True)
                stock_data.append(df)

            batch_count += 1
            print(batch_count, batch_size, len(stock_data))
            if batch_count == batch_size:
                print("update data to parquet")
                self.update_data_to_parquet(stock_data)
                batch_count = 0
                stock_data = []


        self.update_data_to_parquet(stock_data)
        input("Press any key to quit...")
        self.driver.quit()
        
        return stock_data

    def update_data_to_parquet(self, stock_data: List[pd.DataFrame], folder_path: str = DATADIR):
        # 建立一個字典來存放每個 tier 的新資料
        data_dict = {}

        for df in stock_data:
            for _, row in df.iterrows():
                tier, count, share_units, share_percentage, symbol, datetime = row
                new_row = {
                    "股票代碼": symbol,
                    "日期": datetime,
                    "人數": count,
                    "股數/單位數": share_units,
                    "占集保庫存數比例 (%)": share_percentage
                }
                new_df = pd.DataFrame([new_row])
                new_df.set_index(['股票代碼', '日期'], inplace=True)

                # 將新的資料加入到對應的 tier 中
                if tier in data_dict:
                    data_dict[tier] = pd.concat([data_dict[tier], new_df])
                else:
                    data_dict[tier] = new_df

        # 將每個 tier 的新資料寫入到對應的檔案中
        for tier, new_data in data_dict.items():
            filename = f"{tier}.parquet"
            file_path = os.path.join(folder_path, filename)

            if os.path.exists(file_path):
                existing_df = pd.read_parquet(file_path)
                existing_df.set_index(['股票代碼', '日期'], inplace=True)
                updated_df = pd.concat([existing_df, new_data]).reset_index().drop_duplicates()
            else:
                updated_df = new_data.reset_index()

            updated_df.sort_values(by=['股票代碼', '日期'], inplace=True)
            print(f"Updating {tier}.parquet")
            updated_df.to_parquet(file_path, index=False)
