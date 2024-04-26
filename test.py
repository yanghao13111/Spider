from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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

# 現在應該可以抓取頁面上的數據了，可以使用Selenium的API或者把頁面的HTML內容傳給BeautifulSoup來解析
data = driver.page_source

# 創建一個 BeautifulSoup 對象，將HTML內容轉換為Python對象
soup = BeautifulSoup(data, 'html.parser')

# # 找到證券代號和證券名稱
# stock_info = soup.find('div', id='stock_info').text.strip()
# # 找到資料日期
# date_info = soup.find('div', id='date_info').text.strip()
# # 找到包含表格的div元素
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

# input("Press any key to quit...")
# driver.quit()ß