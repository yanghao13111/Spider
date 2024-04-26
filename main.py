from selenium import webdriver


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("http://www.google.com")
    input("Press any key to quit...")
    driver.quit()