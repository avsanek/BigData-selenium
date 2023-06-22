import re
import requests
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def rename_title(title):
    pattern = r'(\b([\dA-Z]+\S)?([А-Яа-я]+)(\S[\dA-Z]+)?\b[А-Яа-я ]+)*((\b(?=\w*[a-zA-Z])(?=\w*\d)\w+\b|\b[A-Za-z]+\b).+)'
    # selects only English words, numbers and skips everything unnecessary
    new_title = re.search(pattern, title)
    return new_title.group(5).replace('&', '%26') if new_title is not None else 'no_required_characters'


# def rename_title(title):
#     pattern = r'([A-Z\d/-]{7,})'       # id search
#     new_title = re.search(pattern, title)
#     return new_title.group(1).replace('&', '%26') if new_title is not None else 'no_required_characters'


try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument("window-size=1400,1024")  # change the window to capture all the buttons
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(5)
    browser.get('https://i-on.by/admin/baza/?route=common/login')  # main site
    browser.find_element(By.CSS_SELECTOR, 'div.content input[name="username"]').send_keys('')
    browser.find_element(By.CSS_SELECTOR, 'div.content input[name="password"]').send_keys('')
    browser.find_element(By.CSS_SELECTOR, 'div.content a.knopka_blue').click()  # log in

    url_search = browser.find_element(By.CSS_SELECTOR, '#link a[href]')
    browser.get(url_search.get_attribute("href"))  # Go to the search page
    browser.find_element(By.CSS_SELECTOR, 'table.list_z td.td-7 a[href]').click()  # changing the sorting
    next_page = browser.find_element(By.CSS_SELECTOR, 'div.links a[href]').get_attribute(
        "href")  # save the future page for the next step
    next_page = next_page.replace('page=2', 'page=103')  # change the page to the last page to move from the last to
    # the first, because otherwise there will be a loss of data
    count = 0  # counting of found links
    count_page = 0  # counting pages traveled

    while True:
        elements = WebDriverWait(browser, 200).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table.list tr')))  # we are waiting for all the
        # fields we need to load, because the site can sometimes slow down
        for element in elements:
            title = browser.find_element(By.CSS_SELECTOR, f'[id="{element.get_attribute("id")}"] .td-3 input')
            need_title = rename_title(title.get_attribute('value'))
            # change the name of the product to the necessary one
            if need_title != 'no_required_characters':  # If there is no match, skip
                site = requests.get(f'https://www.onliner.by/sdapi/catalog.api/search/products?query={need_title}')
                # looking for the received item on api-marcet
                if 0 < site.json()['total'] <= 3:  # we take those products that are from 1 to 3
                    count += 1
                    product = site.json()['products'][0]['html_url']  # need product
                    browser.find_element(By.CSS_SELECTOR, f'[id="{element.get_attribute("id")}"] input.fast').send_keys(
                        product)  # adds a product to the site

        count_page += 1
        print(count_page, count)
        page_num = int(next_page.split('=')[-1]) - 1  # subtract from the last page -1
        next_page = next_page.replace(f'page={page_num + 1}', f'page={page_num}')  # change the page
        browser.get(next_page)  # go to the next page


except TimeoutException:
    print('base completed!')
    print(f'Pages Passed: {count_page} Products found: {count} Stopped Work on the page {page_num + 1}')

finally:
    browser.quit()
