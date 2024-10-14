import pandas as pd
import os
import time


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(PROJECT_ROOT, 'database')

# 讀取並打印 1-999.parquet
file_path = os.path.join(DATADIR, '1-999.parquet')

# 記錄開始時間
start_time = time.time()
df = pd.read_parquet(file_path)
# 記錄結束時間
end_time = time.time()

# 計算並打印讀取檔案所花費的時間
elapsed_time = end_time - start_time
print(f"讀取檔案所花費的時間: {elapsed_time} 秒")

print(df)


# # 設定 pandas 顯示所有的行和列
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

# # 找出每個股票代碼的最新日期
# latest_dates = df.groupby('股票代碼')['日期'].max()

# # 找出每個日期的第一和最後一個股票代碼
# result = df.groupby('日期')['股票代碼'].apply(lambda x: pd.Series([x.iloc[0], x.iloc[-1]], index=['first', 'last'])).reset_index()

# # 打印出每個股票代碼的最新日期
# print(result)

