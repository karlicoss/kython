def scrape(url: str):
    import requests
    from bs4 import BeautifulSoup # type: ignore
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    return soup

def get_chrome_driver(headless=True, profile_dir=None):
    from selenium import webdriver # type: ignore
    from selenium.webdriver.chrome.options import Options # type: ignore

    options = Options()
    if headless:
        options.add_argument('--headless')
    if profile_dir is not None:
        options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    return webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", chrome_options=options)

def scrape_dynamic(url: str, wait=None, *args, **kwargs) -> str:
    driver = get_chrome_driver(*args, **kwargs)
    try:
        driver.get(url)
        if wait is not None:
            import time
            time.sleep(wait)
            # driver.implicitly_wait(wait) # TOOD shit, implicit wait doesn't work...
        return driver.page_source
    finally:
        driver.quit()
