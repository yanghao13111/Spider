from tdcc.tdcc_base import TdccBase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd

class EquityDispersionTable(TdccBase):
    def __init__(self, data):
        super().__init__(data)
        self.stock_codes = self.df['證券代號'].tolist()

    def scrape(self):
        dates = [date.get_attribute('value') for date in Select(self.driver.find_element(By.ID, 'scaDate')).options]

        for stock_code in self.stock_codes:
            for date in dates:
                # ---------------------- date ----------------------
                select_element = Select(self.driver.find_element(By.ID, 'scaDate'))
                select_element.select_by_value(date)
                print(stock_code, select_element.first_selected_option.text)
                # ---------------------- stock code ----------------------
                input_element = self.driver.find_element(By.ID, 'StockNo')
                input_element.clear() 
                input_element.send_keys(stock_code)
                input_element.send_keys(Keys.RETURN)

                sleep(1)
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


                for row in rows:
                    print('\t'.join(row))
                # transform data into dataframe
                if len(rows) > 1 and rows[1][0] != "查無此資料":
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                    df.reset_index(drop=True, inplace=True)
                    print(df)

                print('----------------------------------------')
            print('========================================')

        input("Press any key to quit...")
        self.driver.quit()

    def upate_data(self):
        dates = [date.get_attribute('value') for date in Select(self.driver.find_element(By.ID, 'scaDate')).options]

        # 只選擇最新的日期
        latest_date = dates[0]

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

            sleep(1)
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

            for row in rows:
                print('\t'.join(row))
            # transform data into dataframe
            if len(rows) > 1 and rows[1][0] != "查無此資料":
                df = pd.DataFrame(rows[1:], columns=rows[0])
                df.reset_index(drop=True, inplace=True)
                print(df)

            print('----------------------------------------')
        print('========================================')

        input("Press any key to quit...")
        self.driver.quit()