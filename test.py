from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup
from time import sleep

url = 'https://www.tdcc.com.tw/portal/zh/smWeb/qryStock'

# 初始化webdriver
driver = webdriver.Chrome()

# 輸入網站地址
driver.get(url)

# 網頁可能需要一些時間來載入JavaScript生成的內容，因此等待幾秒鐘
sleep(1)

# 找到輸入框，輸入查詢內容
input_element = driver.find_element(By.ID, 'StockNo')
input_element.send_keys('2330')
input_element.send_keys(Keys.RETURN)

# 再次等待，直到期望的元素出現
sleep(1)

# 找到日期選擇器
select_element = Select(driver.find_element(By.ID, 'scaDate'))

# 獲取所有的日期選項
options = select_element.options

# 獲取所有的日期選項的值
option_values = [option.get_attribute('value') for option in select_element.options]

for value in option_values:
    # 重新獲取 select_element 的參考
    select_element = Select(driver.find_element(By.ID, 'scaDate'))

    # 選擇一個日期
    select_element.select_by_value(value)

    # print date
    print(select_element.first_selected_option.text)

    # 重新獲取 input_element 的參考
    input_element = driver.find_element(By.ID, 'StockNo')

    # # 清除並輸入查詢內容
    input_element.clear() 
    input_element.send_keys('2330')
    input_element.send_keys(Keys.RETURN)

    sleep(1)
    data = driver.page_source
    soup = BeautifulSoup(data, 'html.parser')

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

    # print(stock_info)
    # print(date_info)
    for row in rows:
        print('\t'.join(row))
    print('----------------------------------------')

input("Press any key to quit...")
driver.quit()