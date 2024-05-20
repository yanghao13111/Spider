import os
import pandas as pd
from selenium import webdriver

PROJECT_ROOT = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))

class TdccBase:
    def __init__(self, data):
        self.df = pd.read_csv(os.path.join(PROJECT_ROOT, data), dtype=str)
        self.url = 'https://www.tdcc.com.tw/portal/zh/smWeb/qryStock'
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    # for the first time, run this method
    def scrape(self):
        raise NotImplementedError
    
    def upate_data(self):
        raise NotImplementedError