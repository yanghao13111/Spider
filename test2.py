import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

df = pd.read_csv(os.path.join(DATA_DIR, 'stock_code.csv'))
stock_codes = df['證券代號'].tolist()

# 啟動瀏覽器並打開網頁
url = 'https://www.tdcc.com.tw/portal/zh/smWeb/qryStock'
# 初始化webdriver
driver = webdriver.Chrome()
# 輸入網站地址
driver.get(url)

option_values = [option.get_attribute('value') for option in Select(driver.find_element(By.ID, 'scaDate')).options]

for stock_code in stock_codes:
    for value in option_values:
        # 重新獲取 select_element 的參考
        select_element = Select(driver.find_element(By.ID, 'scaDate'))
        # 選擇一個日期
        select_element.select_by_value(value)
        print(stock_code, select_element.first_selected_option.text)

        # 重新獲取 input_element 的參考
        input_element = driver.find_element(By.ID, 'StockNo')
        # 清除並輸入查詢內容
        input_element.clear() 
        input_element.send_keys(stock_code)
        input_element.send_keys(Keys.RETURN)

        sleep(1)
        data = driver.page_source
        soup = BeautifulSoup(data, 'html.parser')

        data = driver.page_source
        soup = BeautifulSoup(data, 'html.parser')

        # 在這裡處理和儲存網頁內容...
        # ----------------------------------------table----------------------------------------
        table_div = soup.find('div', class_='table-responsive')
        # 從div元素中提取表格
        table = table_div.find('table')
        # 初始化一個空列表來存儲所有的行
        rows = []
        # 首先，找到表頭並提取其內容
        thead = table.find('thead')
        header_cells = thead.find_all('th')
        header = [cell.text.strip() for cell in header_cells]
        rows.append(header)
        # 遍歷表格的每一行
        for row in table.find_all('tr'):
            # 提取行中的所有單元格
            cells = row.find_all('td')
            # 如果這一行有單元格
            if cells:
                # 提取每個單元格的文本並將其添加到這一行的列表中
                rows.append([cell.text.strip() for cell in cells])

        for row in rows:
            print('\t'.join(row))
        # 檢查是否有資料
        if len(rows) > 1 and rows[1][0] != "查無此資料":
            # 轉換為 DataFrame 並印出
            df = pd.DataFrame(rows[1:], columns=rows[0])
            df.reset_index(drop=True, inplace=True)
            # 將 DataFrame 寫入 CSV 文件
            # df.to_csv(os.path.join(DATA_DIR, f'{stock_code}_{value}.csv'), index=False)
            print(df)

        print('----------------------------------------')
    print('========================================')

input("Press any key to quit...")
driver.quit()