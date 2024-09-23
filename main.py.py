from selenium import webdriver
from mops.financial_news_scraper import FinancialNewsScraper


if __name__ == "__main__":
    data = 'stock_code.csv'
    fns = FinancialNewsScraper(data)
    # fns.scrape()
    fns.start_scraping()