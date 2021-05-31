import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

try:
    url = 'https://rent.591.com.tw/?kind=0&region=15'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    time.sleep(3)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.select('.listLeft .infoContent h3 a')
    #    print(elements)
    for e in elements:
        print(e.get("href"))
    print('ok')
    driver.find_element_by_class_name('area-box-close').click()

    driver.find_element_by_class_name('pageNum-form').click()
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.select('.listLeft .infoContent h3 a')
    url = 'https:' + elements[0].get("href")[1:]
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.select('.avatarRight i')
    print(elements[0].text)

    elements = soup.select('.attr li')
    for e in elements:
        print(e.text)

    elements = soup.select('.houseIntro')
    print(elements[0].text)

    elements = soup.select('.labelList li')
    for e in elements:
        print(e.text)

    elements = soup.select('.num img')
    print(elements[0].get("src"))


finally:
    time.sleep(3)
    print('ok')
    driver.quit()
