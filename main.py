from selenium import webdriver
from tdcc.equity_dispersion_table import EquityDispersionTable


if __name__ == "__main__":
    data = 'stock_code.csv'
    ed = EquityDispersionTable(data)
    ed.upate_data()