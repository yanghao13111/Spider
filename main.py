from selenium import webdriver
from tdcc.equity_dispersion_table import EquityDispersionTable


if __name__ == "__main__":
    data = 'stock_code.csv'
    ed = EquityDispersionTable(data)
    # df = ed.upate_data()
    # ed.update_data_to_parquet(df)
    ed.scrape()