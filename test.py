import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(PROJECT_ROOT, 'database')

# 讀取並打印 1-999.parquet
file_path = os.path.join(DATADIR, '1-999.parquet')
df = pd.read_parquet(file_path)
# print(df.columns)
# print(df)

# 將 '日期' 欄位轉換為 datetime 類型
df['日期'] = pd.to_datetime(df['日期'])

# 找出每個股票代碼的最新日期
latest_dates = df.groupby('股票代碼')['日期'].max()

# 打印出每個股票代碼的最新日期
print(latest_dates)