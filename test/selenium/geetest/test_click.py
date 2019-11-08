from selenium import webdriver
from selenium.webdriver.common.by import By
from minitools.selenium.geetest import ClickSelenium
from selenium.webdriver.support import expected_conditions as EC


class GongShang(ClickSelenium):

    def __init__(self):
        self.driver = webdriver.Chrome('D:\chromedriver.exe')
        self.driver.get("http://www.gsxt.gov.cn/index.html")
        self.init_property()

    def capture_interface(self):
        search = self.waiter.until(EC.element_to_be_clickable((By.ID, 'keyword')))
        submit = self.waiter.until(EC.element_to_be_clickable((By.ID, 'btn_query')))
        self.sleep(2)
        search.clear()
        search.send_keys("武汉数博科技")
        self.sleep(2)
        submit.click()

    def calculate_track(self, picture):
        """How to get track???"""

    def check(self):
        self.waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.search_logo_100000')))
        element = self.driver.find_element_by_xpath('//*[@class="search_list_item db"][1]')
        print(element.get_attribute('href'))
        print(self.driver.get_cookies())


if __name__ == '__main__':
    GongShang().run()
