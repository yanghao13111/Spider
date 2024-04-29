import pandas as pd
import os
import sys

# 設定工作目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# 讀取CSV文件
df = pd.read_csv(os.path.join(DATA_DIR, 'TDCC_OD_1-5.csv'))

# 提取"證券代號"列的唯一值
unique_codes = df['證券代號'].unique()

# 將唯一值寫入新的CSV文件
pd.DataFrame(unique_codes, columns=['證券代號']).to_csv(os.path.join(DATA_DIR, 'stock_code.csv'), index=False)