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
        stock_data = []

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


                sleep(0.1)
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

            
        # print(stock_data)
        input("Press any key to quit...")
        self.driver.quit()
            
        return stock_data

    def upate_data(self):
        dates = [date.get_attribute('value') for date in Select(self.driver.find_element(By.ID, 'scaDate')).options]

        # 只選擇最新的日期
        latest_date = dates[0]
        stock_data = []

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

            sleep(0.1)
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

        
        input("Press any key to quit...")
        self.driver.quit()
        
        return stock_data

    def update_data_to_parquet(self, stock_data: List[pd.DataFrame], folder_path: str = DATADIR):
        
        for df in stock_data:
            for _, row in df.iterrows():
                tier, count, share_units, share_percentage, symbol, datetime = row
                filename = f"{tier}.parquet"
                file_path = os.path.join(folder_path, filename)
                new_row = {
                        "股票代碼": symbol,
                        "日期": datetime,
                        "人數": count,
                        "股數/單位數": share_units,
                        "占集保庫存數比例 (%)": share_percentage
                    }
                new_df = pd.DataFrame([new_row])    


                if os.path.exists(file_path):
                    existing_df = pd.read_parquet(file_path)
                    # 將 'datetime' 和 'symbol' 設定為索引
                    existing_df.set_index(['股票代碼', '日期'], inplace=True)
                    new_df.set_index(['股票代碼', '日期'], inplace=True)
                    updated_df = pd.concat([existing_df, new_df])
                    updated_df = updated_df.drop_duplicates()
                    # sort
                    updated_df.sort_values(by=['股票代碼', '日期'], inplace=True)
                    updated_df.reset_index(inplace=True)
                    updated_df.to_parquet(file_path, index=False)
                else:
                    # sort
                    new_df.sort_values(by=['股票代碼', '日期'], inplace=True)
                    new_df.to_parquet(file_path, index=False)