import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(PROJECT_ROOT, 'database')

# 讀取並打印 1-999.parquet
file_path = os.path.join(DATADIR, '1-999.parquet')
df = pd.read_parquet(file_path)
print(df.columns)
print(df)