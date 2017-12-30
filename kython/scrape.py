import requests


def scrape(url: str):
    from bs4 import BeautifulSoup # type: ignore
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    return soup


def scrape_dynamic(url: str) -> str:
    from selenium import webdriver # type: ignore
    from selenium.webdriver.remote.webdriver import WebDriver # type: ignore
    from selenium.webdriver.common.by import By # type: ignore
    from selenium.webdriver.support.ui import WebDriverWait # type: ignore
    from selenium.webdriver.support import expected_conditions as EC # type: ignore
    try:
        driver: WebDriver = webdriver.PhantomJS(executable_path="/L/soft/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
        # driver: WebDriver = webdriver.Chrome(executable_path="/L/soft/chromedriver")
        driver.get(url)
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "nutrition"))
        )
        # driver.implicitly_wait(20)
        return driver.page_source
    finally:
        driver.quit()
